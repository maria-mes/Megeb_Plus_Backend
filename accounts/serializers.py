from rest_framework import serializers

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
            "is_active",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField()  # explicit field, no auto UniqueValidator

    class Meta:
        model = User
        fields = ["full_name", "email", "phone", "password", "confirm_password"]
    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if not attrs.get("phone"):
            raise serializers.ValidationError({"phone": "Phone number is required."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        email = validated_data.pop("email", None)
        phone = validated_data.get("phone")
        password = validated_data.pop("password")

        user = User.objects.filter(phone=phone).first()
        if user:
            user.full_name = validated_data.get("full_name", user.full_name)
            user.email = email or user.email
            user.set_password(password)
            user.is_active = False
            user.is_verified = False
            user.save()
            return user

        return User.objects.create_user(
            phone=phone,
            password=password,
            full_name=validated_data.get("full_name"),
            email=email,
            is_active=False,
            is_verified=False,
        )


class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs