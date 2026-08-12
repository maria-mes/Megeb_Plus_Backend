
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    SendOTPSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from .services.afromessage import send_otp, verify_otp
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
            raise serializers.ValidationError({"detail": "This account is inactive."})

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
        return Response(
            UserSerializer(request.user).data
        )

class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "Registration successful.",
                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "phone": user.phone,
                        "is_verified": user.is_verified
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
class LoginView(APIView):

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class SendOTPView(APIView):

    def post(self, request):

        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data["phone"]

        result = send_otp(phone)

        if result.get("acknowledge") != "success":
            return Response(
                {
                    "detail": "Failed to send OTP.",
                    "response": result
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_id = result["response"]["verificationId"]

        return Response(
            {
                "message": "OTP sent successfully.",
                "verificationId": verification_id
            },
            status=status.HTTP_200_OK
        )

class VerifyOTPView(APIView):

    def post(self, request):

        phone = request.data.get("phone")
        otp = request.data.get("otp")
        verification_id = request.data.get("verificationId")

        if not phone:
            return Response(
                {
                    "detail": "Phone number is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not otp:
            return Response(
                {
                    "detail": "OTP is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verification_id:
            return Response(
                {
                    "detail": "Verification ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        result = verify_otp(
            phone,
            otp,
            verification_id
        )

        if result.get("acknowledge") != "success":
            return Response(
                {
                    "detail": "Invalid or expired OTP.",
                    "response": result
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "OTP verified successfully."
            },
            status=status.HTTP_200_OK
        )