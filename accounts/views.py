from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from health.models import HealthProfile

from .models import PhoneOTP, User
from .serializers import RegisterSerializer, ResetPasswordSerializer, UserSerializer
from .utils import generate_otp, send_sms


class CustomTokenObtainPairSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get("phone")
        password = attrs.get("password")

        user = authenticate(phone=phone, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid phone number or password."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "Account not activated. Verify your phone first."})

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
        }


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        otp_code = generate_otp()

        PhoneOTP.objects.filter(phone=user.phone, purpose=PhoneOTP.PURPOSE_REGISTER).delete()
        otp_record = PhoneOTP.objects.create(
            phone=user.phone,
            otp_code=otp_code,
            purpose=PhoneOTP.PURPOSE_REGISTER,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        send_sms(user.phone, f"Your Megeb+ verification code is {otp_code}")

        return Response(
            {
                "message": "OTP sent. Please verify your phone.",
                "phone": user.phone,
                "requires_otp_verification": True,
                "otp": otp_record.otp_code,
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        otp_code = request.data.get("otp")
        purpose = request.data.get("purpose", PhoneOTP.PURPOSE_REGISTER)

        if not phone or not otp_code:
            return Response({"detail": "Phone and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        otp_record = (
            PhoneOTP.objects.filter(phone=phone, purpose=purpose, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp_record or not otp_record.is_valid():
            return Response({"detail": "OTP is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.otp_code != otp_code:
            otp_record.attempts += 1
            otp_record.save()
            return Response({"detail": "Incorrect OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp_record.is_used = True
        otp_record.save()

        if purpose == PhoneOTP.PURPOSE_REGISTER:
            user = User.objects.filter(phone=phone).first()
            if not user:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            user.is_active = True
            user.is_verified = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Phone verified successfully.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response({"message": "OTP verified successfully.", "phone": phone, "ready_for_reset": True}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        purpose = request.data.get("purpose", PhoneOTP.PURPOSE_REGISTER)

        if not phone:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        otp_code = generate_otp()
        PhoneOTP.objects.filter(phone=phone, purpose=purpose).delete()

        PhoneOTP.objects.create(
            phone=phone,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        send_sms(phone, f"Your Megeb+ verification code is {otp_code}")
        return Response({"message": "OTP resent successfully."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        if not phone:
            return Response({"detail": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        otp_code = generate_otp()
        PhoneOTP.objects.filter(phone=phone, purpose=PhoneOTP.PURPOSE_RESET_PASSWORD).delete()

        PhoneOTP.objects.create(
            phone=phone,
            otp_code=otp_code,
            purpose=PhoneOTP.PURPOSE_RESET_PASSWORD,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        send_sms(phone, f"Your Megeb+ password reset code is {otp_code}")
        return Response({"message": "Password reset OTP sent."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone"]
        otp_code = serializer.validated_data["otp"]
        password = serializer.validated_data["password"]

        otp_record = (
            PhoneOTP.objects.filter(phone=phone, purpose=PhoneOTP.PURPOSE_RESET_PASSWORD, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not otp_record or not otp_record.is_valid():
            return Response({"detail": "OTP is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

        if otp_record.otp_code != otp_code:
            return Response({"detail": "Incorrect OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(password)
        user.save()

        otp_record.is_used = True
        otp_record.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


class HealthProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile, _ = HealthProfile.objects.get_or_create(user=request.user)

        for field in [
            "age",
            "gender",
            "height_cm",
            "weight_kg",
            "activity_level",
            "medical_conditions",
            "allergies",
            "dietary_preferences",
        ]:
            if field in request.data:
                setattr(profile, field, request.data[field])

        profile.save()

        return Response(
            {
                "message": "Health profile saved.",
                "profile": {
                    "age": profile.age,
                    "gender": profile.gender,
                    "height_cm": profile.height_cm,
                    "weight_kg": profile.weight_kg,
                    "activity_level": profile.activity_level,
                    "medical_conditions": profile.medical_conditions,
                    "allergies": profile.allergies,
                    "dietary_preferences": profile.dietary_preferences,
                },
            },
            status=status.HTTP_200_OK,
        )