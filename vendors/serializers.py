import json

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    VendorApplication,
    VendorProfile,
    VendorProduct,
)

User = get_user_model()


class VendorProductSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = VendorProduct

        fields = [
            "id",
            "vendor",
            "name",
            "description",
            "price",
            "category",
            "photo",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "vendor",
            "created_at",
            "updated_at",
        ]


class VendorApplicationSerializer(
    serializers.ModelSerializer
):

    owner_name = serializers.CharField(
        source="user.full_name",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    phone = serializers.CharField(
        source="user.phone",
        read_only=True,
    )

    products = serializers.SerializerMethodField()

    class Meta:
        model = VendorApplication

        fields = [
            "id",
            "user",
            "owner_name",
            "email",
            "phone",
            "business_name",
            "business_address",
            "business_type",
            "license_number",
            "license_document",
            "food_safety_certificate",
            "owner_id_document",
            "status",
            "ai_status",
            "ai_score",
            "ai_result",
            "rejection_reason",
            "reviewed_at",
            "products",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "status",
            "ai_status",
            "ai_score",
            "ai_result",
            "rejection_reason",
            "reviewed_at",
            "created_at",
            "updated_at",
            "products",
        ]

    def get_products(self, obj):

        profile = getattr(
            obj.user,
            "vendor_profile",
            None
        )

        if not profile:
            return []

        return VendorProductSerializer(
            profile.products.all(),
            many=True,
            context=self.context,
        ).data


class VendorProfileSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = VendorProfile

        fields = [
            "id",
            "user",
            "business_name",
            "business_address",
            "business_type",
            "is_verified",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "is_verified",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PublicVendorSerializer(
    serializers.ModelSerializer
):
    """
    Public-facing vendor listing (for the mobile Vendors screen).

    Only exposes approved/active vendors — callers are expected to
    filter the queryset to is_verified=True, is_active=True before
    using this serializer.

    Note: VendorProfile currently has no logo/image or description
    field, so those aren't included here. productCount is provided
    as a lightweight signal of how much a vendor has listed.
    """

    id = serializers.IntegerField(
        read_only=True
    )

    businessName = serializers.CharField(
        source="business_name",
        read_only=True,
    )

    businessType = serializers.CharField(
        source="business_type",
        read_only=True,
    )

    address = serializers.CharField(
        source="business_address",
        read_only=True,
    )

    productCount = serializers.SerializerMethodField()

    class Meta:
        model = VendorProfile

        fields = [
            "id",
            "businessName",
            "businessType",
            "address",
            "productCount",
        ]

    def get_productCount(self, obj):
        return obj.products.filter(
            is_active=True
        ).count()


class VendorRegistrationSerializer(
    serializers.Serializer
):

    owner_name = serializers.CharField()

    email = serializers.EmailField()

    phone = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    business_name = serializers.CharField()

    business_address = serializers.CharField()

    business_type = serializers.ChoiceField(
        choices=VendorApplication.BUSINESS_TYPE_CHOICES
    )

    license_number = serializers.CharField()

    license_document = serializers.FileField()

    food_safety_certificate = serializers.FileField()

    owner_id_document = serializers.FileField()

    products = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_email(self, value):

        if User.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return value

    def validate_phone(self, value):

        if User.objects.filter(
            phone=value
        ).exists():

            raise serializers.ValidationError(
                "An account with this phone already exists."
            )

        return value

    def validate_license_number(self, value):

        if VendorApplication.objects.filter(
            license_number=value
        ).exists():

            raise serializers.ValidationError(
                "This license number is already registered."
            )

        return value

    def validate_products(self, value):

        if not value:
            return []

        try:

            products = json.loads(value)

        except json.JSONDecodeError:

            raise serializers.ValidationError(
                "Products must be valid JSON."
            )

        if not isinstance(products, list):

            raise serializers.ValidationError(
                "Products must be a list."
            )

        return products