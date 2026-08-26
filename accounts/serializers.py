from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, PendingRegistration, StaffApplication
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

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


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "full_name",
            "phone",
            "password",
            "confirm_password"
        ]

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })

        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class PendingRegistrationSerializer(serializers.ModelSerializer):

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

        if User.objects.filter(phone=data["phone"]).exists():
            raise serializers.ValidationError({
                "phone": "This phone number is already registered."
            })

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        validated_data["password"] = make_password(password)

        return PendingRegistration.objects.create(
            **validated_data
        )


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()


# ---------------------------
# Email flow — user registration (mobile app)
# ---------------------------

class EmailRegisterSerializer(serializers.ModelSerializer):
    """Step 1: role=user registers with email. Stages in PendingRegistration."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = PendingRegistration
        fields = ["full_name", "email", "password", "confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        PendingRegistration.objects.filter(email=data["email"]).delete()

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        validated_data["password"] = make_password(password)
        return PendingRegistration.objects.create(**validated_data)


class SendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=["registration", "password_reset"], default="registration")


class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    purpose = serializers.ChoiceField(choices=["registration", "password_reset"], default="registration")


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        return data


# ---------------------------
# Staff applications — vendor/nutritionist (website), admin review
# ---------------------------

class StaffApplicationSerializer(serializers.ModelSerializer):
    """Vendor/nutritionist submits an application with documents + password."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = StaffApplication
        fields = [
            "full_name", "email", "phone", "role", "password", "confirm_password", "application_data",
            "license_document", "credential_document", "insurance_document", "degree_document",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if data["role"] not in ["nutritionist", "vendor"]:
            raise serializers.ValidationError({"role": "Role must be nutritionist or vendor."})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        if StaffApplication.objects.filter(email=data["email"], status="pending").exists():
            raise serializers.ValidationError({"email": "An application with this email is already pending."})

        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        validated_data["password"] = make_password(password)
        return StaffApplication.objects.create(**validated_data)


class StaffApplicationListSerializer(serializers.ModelSerializer):
    """For admin to view pending applications."""

    class Meta:
        model = StaffApplication
        fields = [
            "id", "full_name", "email", "phone", "role", "application_data",
            "license_document", "credential_document", "insurance_document", "degree_document",
            "status", "created_at",
        ]

