from rest_framework import serializers
from .models import User, PendingRegistration


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

        from django.contrib.auth.hashers import make_password

        validated_data["password"] = make_password(password)

        return PendingRegistration.objects.create(
            **validated_data
        )
        
class SendOTPSerializer(serializers.Serializer):

    phone = serializers.CharField()