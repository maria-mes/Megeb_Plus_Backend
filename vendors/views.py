from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    VendorApplication,
    VendorProfile,
    VendorProduct,
)

from .serializers import (
    VendorRegistrationSerializer,
    VendorApplicationSerializer,
    VendorProfileSerializer,
    VendorProductSerializer,
    PublicVendorSerializer,
)

from .ai_verifier import verify_application


User = get_user_model()


class PublicVendorListView(APIView):
    """
    Public: list all approved, active vendors (for the mobile
    Vendors screen). No authentication required — this is a
    public storefront listing, not vendor-account data.

    Only vendors with is_verified=True and is_active=True are
    returned; pending/unapproved applications never appear here.
    """

    permission_classes = [
        AllowAny
    ]

    def get(self, request):

        vendors = (
            VendorProfile.objects
            .filter(
                is_verified=True,
                is_active=True,
            )
            .order_by("business_name")
        )

        return Response(
            PublicVendorSerializer(
                vendors,
                many=True,
            ).data
        )


class VendorRegistrationView(APIView):

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def post(self, request):

        print("CONTENT TYPE:", request.content_type)
        print("DATA:", request.data)
        print("FILES:", request.FILES)
        print("FILE KEYS:", list(request.FILES.keys()))

        serializer = VendorRegistrationSerializer(
        data=request.data,
        context={"request": request}
        )
        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        products = data.pop(
            "products",
            []
        )

        with transaction.atomic():

            user = User.objects.create_user(
                email=data["email"],
                phone=data["phone"],
                password=data["password"],
                full_name=data["owner_name"],
                role="vendor",
            )

            application = VendorApplication.objects.create(
                user=user,
                business_name=data["business_name"],
                business_address=data["business_address"],
                business_type=data["business_type"],
                license_number=data["license_number"],
                license_document=data["license_document"],
                food_safety_certificate=data[
                    "food_safety_certificate"
                ],
                owner_id_document=data[
                    "owner_id_document"
                ],
            )

            # --------------------------------------------------
            # Create vendor profile.
            # It remains inactive until approval.
            # --------------------------------------------------

            vendor_profile = VendorProfile.objects.create(
                user=user,
                business_name=data["business_name"],
                business_address=data["business_address"],
                business_type=data["business_type"],
                is_verified=False,
                is_active=False,
            )

            # --------------------------------------------------
            # Create submitted products.
            # --------------------------------------------------

            for product in products:

                if not product.get("name"):
                    continue

                VendorProduct.objects.create(
                    vendor=vendor_profile,
                    name=product.get("name", ""),
                    description=product.get(
                        "description",
                        ""
                    ),
                    price=product.get(
                        "price",
                        0
                    ),
                    category=product.get(
                        "category",
                        "Uncategorized"
                    ),
                )

            # --------------------------------------------------
            # Run AI verification.
            # --------------------------------------------------

            ai_result = verify_application(
                application,
                persist=True,
            )

        return Response(
            {
                "message": (
                    "Vendor application submitted successfully."
                ),
                "application": VendorApplicationSerializer(
                    application,
                    context={"request": request},
                ).data,
                "ai_verification": ai_result,
            },
            status=status.HTTP_201_CREATED,
        )
class MyVendorApplicationView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        try:

            application = (
                VendorApplication.objects
                .select_related("user")
                .get(user=request.user)
            )

        except VendorApplication.DoesNotExist:

            return Response(
                {
                    "detail": "Vendor application not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            VendorApplicationSerializer(
                application,
                context={"request": request},
            ).data
        )
class VendorProfileView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        try:

            profile = VendorProfile.objects.get(
                user=request.user
            )

        except VendorProfile.DoesNotExist:

            return Response(
                {
                    "detail": "Vendor profile not found."
                },
                status=404,
            )

        return Response(
            VendorProfileSerializer(profile).data
        )

    def patch(self, request):

        try:

            profile = VendorProfile.objects.get(
                user=request.user
            )

        except VendorProfile.DoesNotExist:

            return Response(
                {
                    "detail": "Vendor profile not found."
                },
                status=404,
            )

        serializer = VendorProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )
class VendorProductListCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get_vendor(self, request):

        try:

            return VendorProfile.objects.get(
                user=request.user
            )

        except VendorProfile.DoesNotExist:

            return None

    def get(self, request):

        vendor = self.get_vendor(request)

        if not vendor:

            return Response(
                {
                    "detail": "Vendor profile not found."
                },
                status=404,
            )

        products = vendor.products.all()

        return Response(
            VendorProductSerializer(
                products,
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request):

        vendor = self.get_vendor(request)

        if not vendor:

            return Response(
                {
                    "detail": "Vendor profile not found."
                },
                status=404,
            )

        if not vendor.is_verified:

            return Response(
                {
                    "detail": (
                        "Your vendor account has not "
                        "been verified yet."
                    )
                },
                status=403,
            )

        serializer = VendorProductSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(
            raise_exception=True
        )

        product = serializer.save(
            vendor=vendor
        )

        return Response(
            VendorProductSerializer(
                product,
                context={"request": request},
            ).data,
            status=201,
        )
class VendorProductDetailView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get_product(
        self,
        request,
        product_id
    ):

        try:

            return VendorProduct.objects.get(
                id=product_id,
                vendor__user=request.user,
            )

        except VendorProduct.DoesNotExist:

            return None

    def patch(self, request, product_id):

        product = self.get_product(
            request,
            product_id
        )

        if not product:

            return Response(
                {
                    "detail": "Product not found."
                },
                status=404,
            )

        serializer = VendorProductSerializer(
            product,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            serializer.data
        )

    def delete(self, request, product_id):

        product = self.get_product(
            request,
            product_id
        )

        if not product:

            return Response(
                {
                    "detail": "Product not found."
                },
                status=404,
            )

        product.delete()

        return Response(
            status=204
        )
class AdminVendorApplicationListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        if request.user.role != "admin":

            return Response(
                {
                    "detail": "Admin access required."
                },
                status=403,
            )

        applications = (
            VendorApplication.objects
            .select_related("user")
            .order_by("-created_at")
        )

        return Response(
            VendorApplicationSerializer(
                applications,
                many=True,
                context={"request": request},
            ).data
        )
class AdminVendorApplicationReviewView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def patch(self, request, application_id):

        if request.user.role != "admin":

            return Response(
                {
                    "detail": "Admin access required."
                },
                status=403,
            )

        try:

            application = (
                VendorApplication.objects
                .select_related("user")
                .get(id=application_id)
            )

        except VendorApplication.DoesNotExist:

            return Response(
                {
                    "detail": "Application not found."
                },
                status=404,
            )

        decision = request.data.get(
            "decision"
        )

        rejection_reason = request.data.get(
            "rejection_reason"
        )

        if decision not in [
            "approved",
            "rejected",
        ]:

            return Response(
                {
                    "detail": (
                        "decision must be "
                        "'approved' or 'rejected'."
                    )
                },
                status=400,
            )

        if decision == "rejected":

            application.status = "rejected"

            application.rejection_reason = (
                rejection_reason
                or "Application rejected by admin."
            )

            application.reviewed_at = timezone.now()

            application.save(
                update_fields=[
                    "status",
                    "rejection_reason",
                    "reviewed_at",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "message": "Vendor application rejected.",
                    "application": VendorApplicationSerializer(
                        application,
                        context={"request": request},
                    ).data,
                }
            )

        # ------------------------------------------------------
        # Approval
        # ------------------------------------------------------

        if application.ai_status not in [
            "verified",
            "needs_review",
        ]:

            return Response(
                {
                    "detail": (
                        "This application failed AI "
                        "verification and cannot be approved."
                    ),
                    "ai_status": application.ai_status,
                    "ai_score": application.ai_score,
                },
                status=400,
            )

        try:

            profile = VendorProfile.objects.get(
                user=application.user
            )

        except VendorProfile.DoesNotExist:

            profile = VendorProfile.objects.create(
                user=application.user,
                business_name=application.business_name,
                business_address=application.business_address,
                business_type=application.business_type,
            )

        profile.is_verified = True
        profile.is_active = True

        profile.save(
            update_fields=[
                "is_verified",
                "is_active",
                "updated_at",
            ]
        )

        application.status = "approved"

        application.reviewed_at = timezone.now()

        application.rejection_reason = None

        application.save(
            update_fields=[
                "status",
                "reviewed_at",
                "rejection_reason",
                "updated_at",
            ]
        )

        # Activate user account too.
        application.user.is_active = True
        application.user.role = "vendor"

        application.user.save(
            update_fields=[
                "is_active",
                "role",
            ]
        )

        return Response(
            {
                "message": (
                    "Vendor application approved."
                ),
                "application": VendorApplicationSerializer(
                    application,
                    context={"request": request},
                ).data,
                "vendor": VendorProfileSerializer(
                    profile
                ).data,
            }
        )