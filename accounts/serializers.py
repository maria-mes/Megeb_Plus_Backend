from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, PendingRegistration, StaffApplication
from django.db.models import Q
from rest_framework_simplejwt.serializers import (
    RefreshToken,
    TokenObtainPairSerializer,
)
from django.utils import timezone
import json


# ============================================================
# USER SERIALIZER
# ============================================================

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "role",
            "profile_picture",
            "is_verified",
        ]


# ============================================================
# REGISTER SERIALIZER
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    email = serializers.EmailField(
        required=False,
        allow_null=True
    )

    phone = serializers.CharField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = PendingRegistration

        fields = [
            "full_name",
            "phone",
            "email",
            "password",
            "confirm_password",
        ]

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if not data.get("phone") and not data.get("email"):
            raise serializers.ValidationError({
                "detail": "Either phone or email is required."
            })

        if data.get("phone") and User.objects.filter(
            phone=data["phone"]
        ).exists():
            raise serializers.ValidationError({
                "phone": "This phone number is already registered."
            })

        if data.get("email") and User.objects.filter(
            email=data["email"]
        ).exists():
            raise serializers.ValidationError({
                "email": "This email is already registered."
            })

        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        validated_data["password"] = make_password(password)

        # Remove an old unfinished registration
        if validated_data.get("phone"):
            PendingRegistration.objects.filter(
                phone=validated_data["phone"]
            ).delete()

        return PendingRegistration.objects.create(
            **validated_data
        )


# ============================================================
# LOGIN SERIALIZER
# ============================================================

class LoginSerializer(serializers.Serializer):

    identifier = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        identifier = attrs.get("identifier")
        password = attrs.get("password")

        # Find user by email OR phone
        user = User.objects.filter(
            Q(email=identifier) |
            Q(phone=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({
                "detail": "Invalid credentials."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "detail": "This account is inactive."
            })

        # Invalidate previous tokens
        user.token_version += 1

        user.save(
            update_fields=["token_version"]
        )

        # Generate JWT
        refresh = RefreshToken.for_user(user)

        refresh["token_version"] = user.token_version

        access = refresh.access_token

        return {
            "refresh": str(refresh),
            "access": str(access),
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
        }


# ============================================================
# CUSTOM JWT SERIALIZER
# ============================================================

class CustomTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    def validate(self, attrs):

        data = super().validate(attrs)

        self.user.token_version += 1

        self.user.save(
            update_fields=["token_version"]
        )

        data["user_id"] = self.user.id
        data["role"] = self.user.role
        data["email"] = self.user.email
        data["phone"] = self.user.phone
        data["token_version"] = self.user.token_version

        return data

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token["role"] = user.role
        token["email"] = user.email
        token["phone"] = user.phone
        token["token_version"] = user.token_version

        return token


# ============================================================
# PENDING REGISTRATION SERIALIZER
# ============================================================

class PendingRegistrationSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = PendingRegistration

        fields = [
            "full_name",
            "phone",
            "password",
            "confirm_password",
        ]

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if User.objects.filter(
            phone=data["phone"]
        ).exists():
            raise serializers.ValidationError({
                "phone": "This phone number is already registered."
            })

        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        validated_data["password"] = make_password(
            password
        )

        return PendingRegistration.objects.create(
            **validated_data
        )


# ============================================================
# SEND PHONE OTP
# ============================================================

class SendOTPSerializer(serializers.Serializer):

    phone = serializers.CharField()

    purpose = serializers.ChoiceField(
        choices=[
            "registration",
            "password_reset",
        ],
        default="registration"
    )


# ============================================================
# EMAIL REGISTRATION
# ============================================================

class EmailRegisterSerializer(
    serializers.ModelSerializer
):
    """
    Step 1:
    Register using email.
    Registration is stored in PendingRegistration.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = PendingRegistration

        fields = [
            "full_name",
            "email",
            "password",
            "confirm_password",
        ]

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        if User.objects.filter(
            email=data["email"]
        ).exists():
            raise serializers.ValidationError({
                "email": "This email is already registered."
            })

        PendingRegistration.objects.filter(
            email=data["email"]
        ).delete()

        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        validated_data["password"] = make_password(
            password
        )

        return PendingRegistration.objects.create(
            **validated_data
        )


# ============================================================
# SEND EMAIL OTP
# ============================================================

class SendEmailOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()

    purpose = serializers.ChoiceField(
        choices=[
            "registration",
            "password_reset",
        ],
        default="registration"
    )


# ============================================================
# VERIFY EMAIL OTP
# ============================================================

class VerifyEmailOTPSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField()

    purpose = serializers.ChoiceField(
        choices=[
            "registration",
            "password_reset",
        ],
        default="registration"
    )


# ============================================================
# RESET PASSWORD
# ============================================================

class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    phone = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_new_password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):

        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({
                "confirm_new_password": "Passwords do not match."
            })

        if not data.get("email") and not data.get("phone"):
            raise serializers.ValidationError({
                "detail": "Email or phone is required."
            })

        if data.get("email") and data.get("phone"):
            raise serializers.ValidationError({
                "detail": "Provide either email or phone, not both."
            })

        return data


# ============================================================
# STAFF APPLICATION SERIALIZER
# VENDOR / NUTRITIONIST
# ============================================================

class StaffApplicationSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used when a vendor or nutritionist
    submits a staff application.

    Supports:
    - Basic information
    - Professional information
    - License information
    - Credential information
    - Insurance information
    - Education information
    - Supporting documents
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = StaffApplication

        fields = [

            # -----------------------------------------
            # Basic information
            # -----------------------------------------

            "full_name",
            "email",
            "phone",
            "role",

            "password",
            "confirm_password",

            # -----------------------------------------
            # Professional information
            # -----------------------------------------

            "current_role",
            "specialization",
            "years_of_experience",

            # -----------------------------------------
            # License information
            # -----------------------------------------

            "license_number",
            "license_jurisdiction",
            "license_expiration_date",

            # -----------------------------------------
            # Credential information
            # -----------------------------------------

            "credential_type",
            "credential_number",

            # -----------------------------------------
            # Insurance information
            # -----------------------------------------

            "insurance_provider",
            "policy_number",
            "insurance_expiration_date",
            "coverage_limit",

            # -----------------------------------------
            # Education information
            # -----------------------------------------

            "degree",
            "institution",
            "field_of_study",
            "graduation_year",

            # -----------------------------------------
            # Documents
            # -----------------------------------------

            "license_document",
            "credential_document",
            "insurance_document",
            "degree_document",

            # -----------------------------------------
            # Application metadata
            # -----------------------------------------

            "submitted_at",
            "created_at",
            "updated_at",
            "status",

            # -----------------------------------------
            # AI verification
            # -----------------------------------------

            "ai_status",
            "ai_score",
            "ai_result",

            # -----------------------------------------
            # Review information
            # -----------------------------------------

            "rejection_reason",
            "reviewed_at",
        ]

        read_only_fields = [
            "submitted_at",
            "created_at",
            "updated_at",
            "status",
            "ai_status",
            "ai_score",
            "ai_result",
            "rejection_reason",
            "reviewed_at",
        ]

    def to_internal_value(self, data):
        """
        Convert the frontend's application_data JSON object
        into the individual StaffApplication model fields.

        The frontend sends application_data as a JSON string
        inside multipart/form-data.
        """

        data = data.copy()

        raw_application_data = data.get(
            "application_data"
        )

        if not raw_application_data:
            raise serializers.ValidationError({
                "application_data": "This field is required."
            })

        if isinstance(raw_application_data, str):
            try:
                application_data = json.loads(
                    raw_application_data
                )
            except json.JSONDecodeError:
                raise serializers.ValidationError({
                    "application_data": (
                        "Invalid JSON. Check the JSON format."
                    )
                })
        else:
            application_data = raw_application_data

        if not isinstance(application_data, dict):
            raise serializers.ValidationError({
                "application_data": (
                    "Must be a JSON object."
                )
            })

        mapping = {
            "currentRole": "current_role",
            "yearsOfExperience": "years_of_experience",
            "specialization": "specialization",
            "licenseNumber": "license_number",
            "licenseState": "license_jurisdiction",
            "licenseExpiration": "license_expiration_date",
            "credentialType": "credential_type",
            "credentialNumber": "credential_number",
            "insuranceProvider": "insurance_provider",
            "policyNumber": "policy_number",
            "insuranceExpiration": "insurance_expiration_date",
            "coverageLimit": "coverage_limit",
            "degree": "degree",
            "institution": "institution",
            "fieldOfStudy": "field_of_study",
            "graduationYear": "graduation_year",
        }

        for frontend_field, backend_field in mapping.items():

            if frontend_field in application_data:
                data[backend_field] = application_data[
                    frontend_field
                ]

        # Remove application_data because it is not
        # a field in the StaffApplication model.
        data.pop(
            "application_data",
            None
        )

        return super().to_internal_value(data)

    def validate(self, data):

        # -----------------------------------------
        # Password confirmation
        # -----------------------------------------

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        # -----------------------------------------
        # Role validation
        # -----------------------------------------

        if data["role"] not in [
            "nutritionist",
            "vendor",
        ]:
            raise serializers.ValidationError({
                "role": (
                    "Role must be nutritionist or vendor."
                )
            })

        # -----------------------------------------
        # Existing user check
        # -----------------------------------------

        if User.objects.filter(
            email=data["email"]
        ).exists():
            raise serializers.ValidationError({
                "email": (
                    "This email is already registered."
                )
            })

        # -----------------------------------------
        # Existing pending application
        # -----------------------------------------

        if StaffApplication.objects.filter(
            email=data["email"],
            status="pending"
        ).exists():
            raise serializers.ValidationError({
                "email": (
                    "An application with this email "
                    "is already pending."
                )
            })

        return data

    def create(self, validated_data):

        validated_data.pop(
            "confirm_password"
        )

        password = validated_data.pop(
            "password"
        )

        # Hash the applicant's password before storing it.
        validated_data["password"] = make_password(
            password
        )

        # Initial application statuses.
        validated_data["ai_status"] = "pending"
        validated_data["status"] = "pending"

        # Explicit timestamps.
        #
        # This is especially useful because your deployed
        # database previously complained that submitted_at
        # was NULL.
        now = timezone.now()

        validated_data["submitted_at"] = now
        validated_data["updated_at"] = now

        return StaffApplication.objects.create(
            **validated_data
        )


# ============================================================
# STAFF APPLICATION LIST SERIALIZER
# ADMIN
# ============================================================

class StaffApplicationListSerializer(
    serializers.ModelSerializer
):
    """
    Serializer used by admin to view staff applications.
    """

    class Meta:
        model = StaffApplication

        fields = [

            "id",

            # -----------------------------------------
            # Basic information
            # -----------------------------------------

            "full_name",
            "email",
            "phone",
            "role",

            # -----------------------------------------
            # Professional information
            # -----------------------------------------

            "current_role",
            "specialization",
            "years_of_experience",

            # -----------------------------------------
            # License information
            # -----------------------------------------

            "license_number",
            "license_jurisdiction",
            "license_expiration_date",

            # -----------------------------------------
            # Credential information
            # -----------------------------------------

            "credential_type",
            "credential_number",

            # -----------------------------------------
            # Insurance information
            # -----------------------------------------

            "insurance_provider",
            "policy_number",
            "insurance_expiration_date",
            "coverage_limit",

            # -----------------------------------------
            # Education information
            # -----------------------------------------

            "degree",
            "institution",
            "field_of_study",
            "graduation_year",

            # -----------------------------------------
            # Documents
            # -----------------------------------------

            "license_document",
            "credential_document",
            "insurance_document",
            "degree_document",

            # -----------------------------------------
            # Application status
            # -----------------------------------------

            "status",
            "ai_status",
            "ai_score",
            "ai_result",
            "rejection_reason",

            # -----------------------------------------
            # Timestamps
            # -----------------------------------------

            "submitted_at",
            "created_at",
            "updated_at",
            "reviewed_at",
            "reviewed_by",
        ]


# ============================================================
# UPDATE PROFILE
# ============================================================

class UpdateProfileSerializer(
    serializers.ModelSerializer
):
    """
    Allows a logged-in user to update their
    basic profile information.
    """

    class Meta:
        model = User

        fields = [
            "full_name",
            "phone",
            "profile_picture",
        ]

    def validate_phone(self, value):

        if value and User.objects.exclude(
            id=self.instance.id
        ).filter(
            phone=value
        ).exists():

            raise serializers.ValidationError(
                "This phone number is already in use."
            )

        return value


# ============================================================
# CHANGE PASSWORD
# ============================================================

class ChangePasswordSerializer(
    serializers.Serializer
):

    current_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_new_password = serializers.CharField(
        write_only=True
    )

    def validate(self, data):

        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({
                "confirm_new_password": (
                    "Passwords do not match."
                )
            })

        return data