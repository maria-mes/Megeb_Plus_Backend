from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.utils.timesince import timesince
from django.db import transaction
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import timedelta

from accounts.models import User, StaffApplication
from accounts.views import _approve_application, _reject_application
from appointments.models import Appointment
from health.models import Food
from vendors.models import VendorApplication, VendorProfile
from payments.models import PaymentTransaction

from .permissions import IsAdminRole
from .models import PlatformSettings
from .serializers import (
    AdminUserSerializer,
    AdminClientListSerializer,
    AdminClientSerializer,
    AdminNutritionistSerializer,
    AdminAppointmentSerializer,
    PlatformSettingsSerializer,
    AdminFoodItemSerializer,
    AdminProfileSerializer,
    AdminFoodVendorSerializer,
)


# ---------------------------
# Users
# ---------------------------

class AdminUserListView(APIView):
    """Admin-only: list all platform users (for Users page)."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        users = User.objects.exclude(role="admin").order_by("-created_at")
        return Response(AdminUserSerializer(users, many=True).data)


class AdminUserDetailView(APIView):
    """Admin-only: suspend/reactivate a user."""

    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["Active", "Suspended"]:
            return Response({"detail": "status must be 'Active' or 'Suspended'."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = (new_status == "Active")
        user.save()

        return Response(AdminUserSerializer(user).data)


# ---------------------------
# Clients
# ---------------------------

class AdminClientListView(APIView):
    """
    Admin-only: list all platform clients (for the Clients page).

    Matches the shape the Next.js /admin/clients page already expects
    (see AdminClientListSerializer) — this view was missing, which broke
    the import in admin/urls.py and took the client-side data with it.
    """

    permission_classes = [IsAdminRole]

    def get(self, request):
        clients = (
            User.objects.filter(role="client")
            .select_related("health_profile")
            .order_by("-created_at")
        )
        return Response(AdminClientListSerializer(clients, many=True).data)


class AdminClientDetailView(APIView):
    """
    Admin-only: view a single client's full profile, and
    suspend/reactivate their account (for the Client detail page).
    """

    permission_classes = [IsAdminRole]

    def get(self, request, client_id):
        client = (
            User.objects.filter(id=client_id, role="client")
            .select_related("health_profile")
            .prefetch_related(
                "client_appointments__nutritionist",
                "client_appointments__consultation",
                "nutrition_goals",
                "nutrition_plans",
            )
            .first()
        )

        if not client:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(AdminClientSerializer(client).data)

    def patch(self, request, client_id):
        client = User.objects.filter(id=client_id, role="client").first()

        if not client:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ["Active", "Suspended"]:
            return Response({"detail": "status must be 'Active' or 'Suspended'."}, status=status.HTTP_400_BAD_REQUEST)

        client.is_active = (new_status == "Active")
        client.save()

        return Response(AdminClientSerializer(client).data)


# ---------------------------
# Nutritionists
# ---------------------------

class AdminNutritionistListView(APIView):
    """Admin-only: list all nutritionist applications, any status (for Nutritionists page)."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        applications = StaffApplication.objects.filter(role="nutritionist").order_by("-created_at")
        return Response(AdminNutritionistSerializer(applications, many=True).data)


class AdminNutritionistDetailView(APIView):
    """Admin-only: approve/reject a nutritionist application from the admin panel."""

    permission_classes = [IsAdminRole]

    def patch(self, request, application_id):
        application = StaffApplication.objects.filter(id=application_id, role="nutritionist").first()

        if not application:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

        if application.status != "pending":
            return Response({"detail": "Application already reviewed."}, status=status.HTTP_400_BAD_REQUEST)

        new_status = request.data.get("status")
        if new_status not in ["Approved", "Rejected"]:
            return Response({"detail": "status must be 'Approved' or 'Rejected'."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == "Approved":
            _approve_application(application, request.user)
        else:
            _reject_application(application, request.user)

        return Response(AdminNutritionistSerializer(application).data)


# ---------------------------
# Appointments
# ---------------------------

class AdminAppointmentListView(APIView):
    """Admin-only: list every appointment across every nutritionist (for Appointments page)."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        appointments = Appointment.objects.select_related(
            "client", "nutritionist"
        ).order_by("-created_at")
        return Response(AdminAppointmentSerializer(appointments, many=True).data)


# ---------------------------
# Reports
# ---------------------------

class AdminReportsView(APIView):
    """Admin-only: platform-wide metrics + monthly signup trend for the Reports page."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

        total_users = User.objects.exclude(role="admin").count()
        total_nutritionists = User.objects.filter(role="nutritionist").count()
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status="completed").count()
        new_users_this_month = User.objects.exclude(role="admin").filter(
            created_at__gte=this_month_start
        ).count()

        # Revenue = platform's own cut (platform_fee), not gross client
        # payments, since nutritionist payouts aren't Megeb+'s revenue.
        revenue_this_month = PaymentTransaction.objects.filter(
            status=PaymentTransaction.STATUS_SUCCESSFUL,
            paid_at__gte=this_month_start,
        ).aggregate(total=Sum("platform_fee"))["total"] or Decimal("0")

        revenue_last_month = PaymentTransaction.objects.filter(
            status=PaymentTransaction.STATUS_SUCCESSFUL,
            paid_at__gte=last_month_start,
            paid_at__lt=this_month_start,
        ).aggregate(total=Sum("platform_fee"))["total"] or Decimal("0")

        if revenue_last_month > 0:
            revenue_change_pct = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
            revenue_change = f"{revenue_change_pct:+.1f}% vs last month"
        else:
            revenue_change = "vs last month: no data"

        metrics = [
            {"label": "Total Users", "value": str(total_users), "change": f"+{new_users_this_month} this month"},
            {"label": "Nutritionists", "value": str(total_nutritionists), "change": "active professionals"},
            {"label": "Appointments", "value": str(total_appointments), "change": f"{completed_appointments} completed"},
            {"label": "New Users", "value": str(new_users_this_month), "change": "this month"},
            {"label": "Revenue", "value": f"ETB {revenue_this_month:,.0f}", "change": revenue_change},
        ]

        six_months_start = (now.replace(day=1) - timedelta(days=150)).replace(day=1)
        signups = (
            User.objects.exclude(role="admin")
            .filter(created_at__gte=six_months_start)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        monthly_signups = [
            {"month": row["month"].strftime("%b"), "value": row["count"]}
            for row in signups
        ]

        return Response({"metrics": metrics, "monthlySignups": monthly_signups})


# ---------------------------
# Dashboard
# ---------------------------

class AdminDashboardStatsView(APIView):
    """
    Admin-only: the 4 headline stat cards on the Dashboard page.
    Shape: {title, value, change, description, icon} — deliberately different
    from AdminReportsView's {label, value, change}, since dashboard/page.tsx
    and reports/page.tsx expect different field names and dashboard needs an
    'icon' key the StatCard component uses to pick a lucide-react icon.
    """

    permission_classes = [IsAdminRole]

    def get(self, request):
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_users = User.objects.exclude(role="admin").count()
        total_nutritionists = User.objects.filter(role="nutritionist").count()
        appointments_this_month = Appointment.objects.filter(created_at__gte=this_month_start).count()
        new_users_this_month = User.objects.exclude(role="admin").filter(
            created_at__gte=this_month_start
        ).count()

        # Revenue = platform's own cut (platform_fee) from successful
        # payments this month. Was hardcoded to "0 ETB" before payments
        # existed — now pulled from payments.PaymentTransaction.
        revenue_this_month = PaymentTransaction.objects.filter(
            status=PaymentTransaction.STATUS_SUCCESSFUL,
            paid_at__gte=this_month_start,
        ).aggregate(total=Sum("platform_fee"))["total"] or Decimal("0")

        stats = [
            {
                "title": "Total Users",
                "value": str(total_users),
                "change": f"+{new_users_this_month}",
                "description": "registered users",
                "icon": "users",
            },
            {
                "title": "Nutritionists",
                "value": str(total_nutritionists),
                "change": "",
                "description": "active professionals",
                "icon": "doctor",
            },
            {
                "title": "Appointments",
                "value": str(appointments_this_month),
                "change": "",
                "description": "this month",
                "icon": "calendar",
            },
            {
                "title": "Revenue",
                "value": f"{revenue_this_month:,.0f} ETB",
                "change": "",
                "description": "this month",
                "icon": "money",
            },
        ]

        return Response(stats)


# ---------------------------
# Settings
# ---------------------------

class AdminSettingsView(APIView):
    """Admin-only: view/edit platform-wide configuration (singleton row)."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        settings_obj = PlatformSettings.load()
        return Response(PlatformSettingsSerializer(settings_obj).data)

    def put(self, request):
        settings_obj = PlatformSettings.load()
        serializer = PlatformSettingsSerializer(settings_obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# Food Database
# ---------------------------

class AdminFoodListView(APIView):
    """
    Admin-only: list/create rows in the shared health.Food catalog
    (for the Food Database page). Reuses the same model the mobile
    app's /foods/ endpoint reads from — no separate admin-only food
    table.
    """

    permission_classes = [IsAdminRole]

    def get(self, request):
        foods = Food.objects.all().order_by("name")
        return Response(AdminFoodItemSerializer(foods, many=True).data)

    def post(self, request):
        serializer = AdminFoodItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# Admin Profile
# ---------------------------

class AdminProfileView(APIView):
    """Admin-only: view/edit the logged-in admin's own account details."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(AdminProfileSerializer(request.user).data)

    def put(self, request):
        serializer = AdminProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminChangePasswordView(APIView):
    """Admin-only: change the logged-in admin's own password."""

    permission_classes = [IsAdminRole]

    def post(self, request):
        current_password = request.data.get("currentPassword")
        new_password = request.data.get("newPassword")

        if not current_password or not new_password:
            return Response(
                {"detail": "currentPassword and newPassword are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if not user.check_password(current_password):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response(
                {"detail": "New password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully."})


# ---------------------------
# Sidebar badges & dashboard verification widget
# ---------------------------

class AdminVerificationRequestsView(APIView):
    """
    Admin-only: pending nutritionist applications, reshaped for the dashboard's
    VerificationRequests widget: {id, name, specialty, submitted}.
    """

    permission_classes = [IsAdminRole]

    def get(self, request):
        status_param = request.query_params.get("status", "pending")
        applications = StaffApplication.objects.filter(
            role="nutritionist", status=status_param
        ).order_by("-created_at")

        data = [
            {
                "id": app.id,
                "name": app.full_name,
                "specialty": (app.application_data or {}).get("specialty")
                or (app.application_data or {}).get("specialization")
                or "",
                "submitted": f"{timesince(app.created_at)} ago",
            }
            for app in applications
        ]

        return Response(data)


class AdminVerificationCountView(APIView):
    """Admin-only: count of nutritionist applications by status, for the sidebar badge."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        status_param = request.query_params.get("status", "pending")
        count = StaffApplication.objects.filter(role="nutritionist", status=status_param).count()
        return Response({"count": count})


class AdminFoodVendorListView(APIView):
    """Admin-only: list food vendor applications."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        status_param = request.query_params.get("status")

        applications = VendorApplication.objects.select_related(
            "user"
        ).order_by("-created_at")

        if status_param:
            applications = applications.filter(status=status_param.lower())

        serializer = AdminFoodVendorSerializer(
            applications,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)


class AdminFoodVendorDetailView(APIView):
    """Admin-only: approve or reject a food vendor application."""

    permission_classes = [IsAdminRole]

    def patch(self, request, application_id):
        application = VendorApplication.objects.select_related("user").filter(
            id=application_id
        ).first()

        if not application:
            return Response(
                {"detail": "Vendor application not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if application.status != "pending":
            return Response(
                {"detail": "Application already reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = request.data.get("status")

        if new_status not in ["Approved", "Rejected"]:
            return Response(
                {"detail": "status must be 'Approved' or 'Rejected'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_status == "Rejected":
            with transaction.atomic():
                application.status = "rejected"
                application.rejection_reason = request.data.get(
                    "reason",
                    "Application rejected by administrator.",
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

                application.user.is_active = False
                application.user.save(update_fields=["is_active"])

                VendorProfile.objects.filter(
                    user=application.user
                ).update(
                    is_verified=False,
                    is_active=False,
                )

            return Response(
                AdminFoodVendorSerializer(
                    application,
                    context={"request": request},
                ).data
            )

        # ------------------------------------------------------
        # Approval
        #
        # FIX: previously any ai_status other than "verified" or
        # "needs_review" (e.g. "failed", from a false-positive
        # regex hard_fail) permanently blocked approval with no
        # way for the admin to override it. Now "failed" returns
        # a 409 with requires_override so the admin can confirm
        # and resend with overrideAi: true to approve anyway.
        # ------------------------------------------------------

        override_ai = bool(request.data.get("overrideAi"))

        if application.ai_status not in ["verified", "needs_review"] and not override_ai:
            return Response(
                {
                    "detail": (
                        "AI verification did not pass for this "
                        "application. Confirm to override and "
                        "approve anyway."
                    ),
                    "ai_status": application.ai_status,
                    "ai_score": application.ai_score,
                    "requires_override": True,
                },
                status=status.HTTP_409_CONFLICT,
            )

        with transaction.atomic():
            profile, _ = VendorProfile.objects.get_or_create(
                user=application.user,
                defaults={
                    "business_name": application.business_name,
                    "business_address": application.business_address,
                    "business_type": application.business_type,
                },
            )

            profile.business_name = application.business_name
            profile.business_address = application.business_address
            profile.business_type = application.business_type
            profile.is_verified = True
            profile.is_active = True
            profile.save()

            application.status = "approved"
            application.reviewed_at = timezone.now()
            application.rejection_reason = ""
            application.save(
                update_fields=[
                    "status",
                    "reviewed_at",
                    "rejection_reason",
                    "updated_at",
                ]
            )

            application.user.is_active = True
            application.user.role = "vendor"
            application.user.save(update_fields=["is_active", "role"])

            profile.products.update(is_active=True)

        return Response(
            AdminFoodVendorSerializer(
                application,
                context={"request": request},
            ).data
        )

class AdminFoodVendorCountView(APIView):
    """Admin-only: count food vendor applications by status."""

    permission_classes = [IsAdminRole]

    def get(self, request):
        status_param = request.query_params.get("status", "pending")

        count = VendorApplication.objects.filter(
            status=status_param.lower()
        ).count()

        return Response({"count": count})