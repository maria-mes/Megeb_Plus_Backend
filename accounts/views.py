from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from rest_framework_simplejwt.views import TokenObtainPairView
import os
import uuid

import boto3
from rest_framework.permissions import AllowAny
from .models import User, OTPVerification, PendingRegistration, StaffApplication
from .models import (
    User,
    OTPVerification,
    PendingRegistration,
    StaffApplication,
)

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    SendOTPSerializer,
    EmailRegisterSerializer,
    SendEmailOTPSerializer,
    VerifyEmailOTPSerializer,
    ResetPasswordSerializer,
    StaffApplicationSerializer,
    StaffApplicationListSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)

from .services.afromessage import send_otp, verify_otp

from .services.email_service import (
    generate_otp,
    send_otp_email,
    send_registration_confirmation_email,
)


# ============================================================
# JWT
# ============================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ============================================================
# CURRENT USER
# ============================================================

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data
        )

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                UserSerializer(request.user).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# REGISTRATION
# ============================================================

class RegisterView(APIView):
    """
    Registration entry point.

    Phone registration:
        /api/auth/register/
        -> AfroMessage SMS OTP

    Email registration:
        /api/auth/register/
        -> Email OTP

    The serializer allows either phone OR email.
    This view now chooses the OTP channel based on what was provided.
    """

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Save pending registration
        # ----------------------------------------------------

        pending = serializer.save()

        # ====================================================
        # PHONE REGISTRATION
        # ====================================================

        if pending.phone:

            result = send_otp(
                pending.phone
            )

            # ------------------------------------------------
            # AfroMessage failed
            # ------------------------------------------------

            if result.get("acknowledge") != "success":

                pending.delete()

                return Response(
                    {
                        "detail": "Failed to send OTP.",
                        "response": result
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Safely get verification ID
            # ------------------------------------------------

            try:
                verification_id = result[
                    "response"
                ]["verificationId"]

            except (KeyError, TypeError):

                pending.delete()

                return Response(
                    {
                        "detail": (
                            "OTP provider returned an "
                            "invalid response."
                        ),
                        "response": result
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # ------------------------------------------------
            # IMPORTANT:
            # Store local OTP verification record.
            #
            # VerifyOTPView depends on this record.
            # ------------------------------------------------

            OTPVerification.objects.create(
                phone=pending.phone,
                channel="phone",
                verification_id=verification_id,
                purpose="registration",
                is_verified=False,
            )

            return Response(
                {
                    "message": (
                        "Registration started. "
                        "OTP sent successfully."
                    ),
                    "verificationId": verification_id,
                    "phone": pending.phone,
                    "purpose": "registration",
                    "channel": "phone",
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # EMAIL REGISTRATION
        # ====================================================

        if pending.email:

            otp = generate_otp()

            # ------------------------------------------------
            # Store local email OTP
            # ------------------------------------------------

            OTPVerification.objects.create(
                email=pending.email,
                otp=otp,
                channel="email",
                purpose="registration",
                is_verified=False,
            )

            # ------------------------------------------------
            # Send email
            # ------------------------------------------------

            try:

                send_otp_email(
                    pending.email,
                    otp,
                    purpose="registration"
                )

            except Exception as e:

                # Remove pending OTP record
                OTPVerification.objects.filter(
                    email=pending.email,
                    otp=otp,
                    channel="email",
                    purpose="registration",
                    is_verified=False,
                ).delete()

                # Remove pending registration
                pending.delete()

                return Response(
                    {
                        "detail": "Failed to send registration email.",
                        "error": str(e),
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response(
                {
                    "message": (
                        "Registration started. "
                        "OTP sent successfully."
                    ),
                    "email": pending.email,
                    "purpose": "registration",
                    "channel": "email",
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # SAFETY FALLBACK
        # ====================================================

        pending.delete()

        return Response(
            {
                "detail": "Phone or email is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# LOGIN
# ============================================================

class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        if serializer.is_valid():

            # LoginSerializer already:
            # - finds the user
            # - validates password
            # - checks active status
            # - creates tokens
            # - handles token_version
            #
            # Do not look the user up again here.

            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# LOGOUT
# ============================================================

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            refresh_token = request.data.get(
                "refresh"
            )

            if refresh_token:

                token = RefreshToken(
                    refresh_token
                )

                token.blacklist()

            return Response(
                {
                    "message": "Logged out successfully."
                },
                status=status.HTTP_200_OK
            )

        except Exception:

            return Response(
                {
                    "detail": (
                        "Invalid or missing refresh token."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# SEND PHONE OTP
# ============================================================

class SendOTPView(APIView):

    def post(self, request):

        serializer = SendOTPSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data[
            "phone"
        ]

        purpose = serializer.validated_data[
            "purpose"
        ]

        # ====================================================
        # REGISTRATION OTP
        # ====================================================

        if purpose == "registration":

            if not PendingRegistration.objects.filter(
                phone=phone
            ).exists():

                return Response(
                    {
                        "detail": (
                            "No pending registration found "
                            "for this phone number."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ====================================================
        # PASSWORD RESET OTP
        # ====================================================

        elif purpose == "password_reset":

            if not User.objects.filter(
                phone=phone,
                is_active=True
            ).exists():

                return Response(
                    {
                        "detail": (
                            "No active account found "
                            "with this phone number."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        # ====================================================
        # SEND OTP
        # ====================================================

        result = send_otp(
            phone
        )

        if result.get("acknowledge") != "success":

            return Response(
                {
                    "detail": "Failed to send OTP.",
                    "response": result
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # GET VERIFICATION ID SAFELY
        # ====================================================

        try:

            verification_id = result[
                "response"
            ]["verificationId"]

        except (KeyError, TypeError):

            return Response(
                {
                    "detail": (
                        "OTP provider returned an "
                        "invalid response."
                    ),
                    "response": result
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # ====================================================
        # STORE OTP RECORD
        # ====================================================

        OTPVerification.objects.create(
            phone=phone,
            channel="phone",
            verification_id=verification_id,
            purpose=purpose,
            is_verified=False,
        )

        return Response(
            {
                "message": "OTP sent successfully.",
                "verificationId": verification_id,
                "phone": phone,
                "purpose": purpose,
                "channel": "phone",
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# VERIFY PHONE OTP
# ============================================================

class VerifyOTPView(APIView):

    def post(self, request):

        phone = request.data.get(
            "phone"
        )

        otp = request.data.get(
            "otp"
        )

        verification_id = request.data.get(
            "verificationId"
        )

        purpose = request.data.get(
            "purpose",
            "registration"
        )

        # ====================================================
        # VALIDATION
        # ====================================================

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

        if purpose not in [
            "registration",
            "password_reset"
        ]:

            return Response(
                {
                    "detail": "Invalid OTP purpose."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # FIND LOCAL OTP RECORD FIRST
        # ====================================================

        record = OTPVerification.objects.filter(
            phone=phone,
            verification_id=verification_id,
            channel="phone",
            purpose=purpose,
            is_verified=False
        ).order_by(
            "-created_at"
        ).first()

        if not record:

            return Response(
                {
                    "detail": (
                        "OTP verification record not found."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # LOCAL EXPIRY CHECK
        # ====================================================

        if record.created_at < (
            timezone.now()
            - timedelta(minutes=10)
        ):

            return Response(
                {
                    "detail": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # VERIFY WITH AFROMESSAGE
        # ====================================================

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

        # ====================================================
        # MARK LOCAL OTP VERIFIED
        # ====================================================

        record.is_verified = True
        record.verified_at = timezone.now()

        record.save(
            update_fields=[
                "is_verified",
                "verified_at"
            ]
        )

        # ====================================================
        # REGISTRATION
        # ====================================================

        if purpose == "registration":

            pending = PendingRegistration.objects.filter(
                phone=phone
            ).first()

            if not pending:

                return Response(
                    {
                        "detail": (
                            "No pending registration found."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Check existing user
            # ------------------------------------------------

            if User.objects.filter(
                phone=phone
            ).exists():

                pending.delete()

                return Response(
                    {
                        "detail": (
                            "This phone number is "
                            "already registered."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Create user
            # ------------------------------------------------

            user = User(
                full_name=pending.full_name,
                phone=pending.phone,
                email=pending.email,
                role="user",
                is_verified=True,
                is_active=True,
                token_version=0,
            )

            # Password is already hashed
            user.password = pending.password

            user.save()

            # ------------------------------------------------
            # Create empty health profile
            # ------------------------------------------------

            from health.models import HealthProfile

            HealthProfile.objects.get_or_create(
                user=user
            )

            # ------------------------------------------------
            # Delete pending registration
            # ------------------------------------------------

            pending.delete()

            # ------------------------------------------------
            # JWT
            # ------------------------------------------------

            refresh = RefreshToken.for_user(
                user
            )

            refresh["role"] = user.role
            refresh["email"] = user.email
            refresh["phone"] = user.phone
            refresh["token_version"] = user.token_version

            access = refresh.access_token

            return Response(
                {
                    "message": "Registration complete.",
                    "registration_complete": True,
                    "requires_health_profile": True,

                    "access": str(access),
                    "refresh": str(refresh),

                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "phone": user.phone,
                        "email": user.email,
                        "role": user.role,
                        "is_verified": user.is_verified,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        # ====================================================
        # PASSWORD RESET
        # ====================================================

        return Response(
            {
                "message": "OTP verified successfully.",
                "phone": phone,
                "purpose": "password_reset"
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# EMAIL REGISTRATION
# ============================================================

class EmailRegisterView(APIView):
    """
    Step 1:

    User registers with email.

    PendingRegistration is created and an email OTP is sent.
    """

    def post(self, request):

        serializer = EmailRegisterSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        pending = serializer.save()

        otp = generate_otp()

        # ----------------------------------------------------
        # Store OTP
        # ----------------------------------------------------

        OTPVerification.objects.create(
            email=pending.email,
            otp=otp,
            channel="email",
            purpose="registration",
            is_verified=False,
        )

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        try:

            send_otp_email(
                pending.email,
                otp,
                purpose="registration"
            )

        except Exception as e:

            OTPVerification.objects.filter(
                email=pending.email,
                otp=otp,
                channel="email",
                purpose="registration",
                is_verified=False,
            ).delete()

            pending.delete()

            return Response(
                {
                    "detail": (
                        "Failed to send registration email."
                    ),
                    "error": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {
                "message": (
                    "OTP sent to email. "
                    "Verify to complete registration."
                ),
                "email": pending.email,
                "purpose": "registration",
                "channel": "email",
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# SEND EMAIL OTP
# ============================================================

class SendEmailOTPView(APIView):
    """
    Send/resend email OTP.

    Used for:
        - registration resend
        - forgot password
    """

    def post(self, request):

        serializer = SendEmailOTPSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data[
            "email"
        ]

        purpose = serializer.validated_data[
            "purpose"
        ]

        # ====================================================
        # PASSWORD RESET
        # ====================================================

        if purpose == "password_reset":

            if not User.objects.filter(
                email=email,
                is_active=True
            ).exists():

                return Response(
                    {
                        "detail": (
                            "No active account found "
                            "with this email."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        # ====================================================
        # REGISTRATION
        # ====================================================

        if purpose == "registration":

            if not PendingRegistration.objects.filter(
                email=email
            ).exists():

                return Response(
                    {
                        "detail": (
                            "No pending registration found "
                            "for this email."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ====================================================
        # GENERATE OTP
        # ====================================================

        otp = generate_otp()

        # ----------------------------------------------------
        # Store OTP
        # ----------------------------------------------------

        OTPVerification.objects.create(
            email=email,
            otp=otp,
            channel="email",
            purpose=purpose,
            is_verified=False,
        )

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        try:

            send_otp_email(
                email,
                otp,
                purpose=purpose
            )

        except Exception as e:

            OTPVerification.objects.filter(
                email=email,
                otp=otp,
                channel="email",
                purpose=purpose,
                is_verified=False,
            ).delete()

            return Response(
                {
                    "detail": "Failed to send OTP email.",
                    "error": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(
            {
                "message": "OTP sent successfully.",
                "email": email,
                "purpose": purpose,
                "channel": "email",
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# VERIFY EMAIL OTP
# ============================================================

class VerifyEmailOTPView(APIView):
    """
    Verifies email OTP.

    Registration:
        PendingRegistration -> User

    Password reset:
        OTP marked verified
    """

    def post(self, request):

        serializer = VerifyEmailOTPSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data[
            "email"
        ]

        otp = serializer.validated_data[
            "otp"
        ]

        purpose = serializer.validated_data[
            "purpose"
        ]

        # ====================================================
        # FIND OTP
        # ====================================================

        record = OTPVerification.objects.filter(
            email=email,
            otp=otp,
            channel="email",
            purpose=purpose,
            is_verified=False
        ).order_by(
            "-created_at"
        ).first()

        if not record:

            return Response(
                {
                    "detail": "Invalid or expired OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # EXPIRY
        # ====================================================

        if record.created_at < (
            timezone.now()
            - timedelta(minutes=10)
        ):

            return Response(
                {
                    "detail": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # MARK VERIFIED
        # ====================================================

        record.is_verified = True
        record.verified_at = timezone.now()

        record.save(
            update_fields=[
                "is_verified",
                "verified_at"
            ]
        )

        # ====================================================
        # REGISTRATION
        # ====================================================

        if purpose == "registration":

            pending = PendingRegistration.objects.filter(
                email=email
            ).first()

            if not pending:

                return Response(
                    {
                        "detail": (
                            "No pending registration "
                            "found for this email."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Prevent duplicate account
            # ------------------------------------------------

            if User.objects.filter(
                email=email
            ).exists():

                pending.delete()

                return Response(
                    {
                        "detail": (
                            "This email is already registered."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ------------------------------------------------
            # Create user
            # ------------------------------------------------

            user = User(
                full_name=pending.full_name,
                email=pending.email,
                role="user",
                is_verified=True,
                is_active=True,
                token_version=0,
            )

            # Password already hashed
            user.password = pending.password

            user.save()

            # ------------------------------------------------
            # Create empty health profile
            # ------------------------------------------------

            from health.models import HealthProfile

            HealthProfile.objects.get_or_create(
                user=user
            )

            # ------------------------------------------------
            # Delete pending registration
            # ------------------------------------------------

            pending.delete()

            # ------------------------------------------------
            # JWT
            # ------------------------------------------------

            refresh = RefreshToken.for_user(
                user
            )

            refresh["role"] = user.role
            refresh["email"] = user.email
            refresh["phone"] = user.phone
            refresh["token_version"] = user.token_version

            access = refresh.access_token

            return Response(
                {
                    "message": "Registration complete.",
                    "registration_complete": False,
                    "requires_health_profile": True,

                    "access": str(access),
                    "refresh": str(refresh),

                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role,
                        "is_verified": user.is_verified,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        # ====================================================
        # PASSWORD RESET
        # ====================================================

        return Response(
            {
                "message": "OTP verified successfully.",
                "email": email,
                "purpose": "password_reset"
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# RESET PASSWORD
# ============================================================

class ResetPasswordView(APIView):
    """
    Final step of forgot-password.

    Supports:
        - email
        - phone
    """

    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data.get(
            "email"
        )

        phone = serializer.validated_data.get(
            "phone"
        )

        new_password = serializer.validated_data[
            "new_password"
        ]

        # ====================================================
        # FIND VERIFIED OTP
        # ====================================================

        if email:

            verified_otp = OTPVerification.objects.filter(
                email=email,
                channel="email",
                purpose="password_reset",
                is_verified=True
            ).order_by(
                "-verified_at"
            ).first()

        else:

            verified_otp = OTPVerification.objects.filter(
                phone=phone,
                channel="phone",
                purpose="password_reset",
                is_verified=True
            ).order_by(
                "-verified_at"
            ).first()

        # ====================================================
        # NO VERIFIED OTP
        # ====================================================

        if not verified_otp:

            return Response(
                {
                    "detail": (
                        "Please verify OTP before "
                        "resetting your password."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # OTP VERIFICATION EXPIRY
        # ====================================================

        if verified_otp.verified_at < (
            timezone.now()
            - timedelta(minutes=15)
        ):

            verified_otp.delete()

            return Response(
                {
                    "detail": (
                        "OTP verification has expired. "
                        "Please verify again."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # FIND USER
        # ====================================================

        if email:

            user = User.objects.filter(
                email=email,
                is_active=True
            ).first()

            if not user:

                return Response(
                    {
                        "detail": (
                            "No active account found "
                            "with this email."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        else:

            user = User.objects.filter(
                phone=phone,
                is_active=True
            ).first()

            if not user:

                return Response(
                    {
                        "detail": (
                            "No active account found "
                            "with this phone number."
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        # ====================================================
        # RESET PASSWORD
        # ====================================================

        user.set_password(
            new_password
        )

        # Increment token version.
        # Invalidates existing JWT tokens.
        user.token_version += 1

        user.save(
            update_fields=[
                "password",
                "token_version"
            ]
        )

        # ====================================================
        # DELETE USED OTP
        # ====================================================

        verified_otp.delete()

        return Response(
            {
                "message": "Password reset successful."
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# STAFF APPLICATIONS
# ============================================================

class IsAdminRole(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


# ============================================================
# STAFF APPLY
# ============================================================

class StaffApplyView(APIView):
    """
    Vendor/nutritionist submits application.

    No account/password is created until approval.
    """

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def post(self, request):

        serializer = StaffApplicationSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        application = serializer.save()

        send_mail(
            subject="Megeb+ Application Received",

            message=(
                f"Hi {application.full_name},\n\n"
                f"We've received your application to join "
                f"Megeb+ as a {application.role}.\n"
                f"Our team will review your credentials "
                f"and get back to you soon."
            ),

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[
                application.email
            ],

            fail_silently=False,
        )

        return Response(
            {
                "message": (
                    "Application submitted. "
                    "You'll be notified by email once reviewed."
                ),
                "application_id": application.id
            },
            status=status.HTTP_201_CREATED
        )


# ============================================================
# PENDING APPLICATIONS
# ============================================================

class PendingApplicationsView(APIView):

    permission_classes = [
        IsAdminRole
    ]

    def get(self, request):

        applications = (
            StaffApplication.objects
            .filter(status="pending")
            .order_by("-created_at")
        )

        return Response(
            StaffApplicationListSerializer(
                applications,
                many=True,
                context={
                    "request": request
                }
            ).data
        )


# ============================================================
# APPROVE APPLICATION
# ============================================================

def _approve_application(
    application,
    reviewer
):
    """
    Shared approval logic.

    Approval:
        StaffApplication
            ->
        User
    """

    phone_to_use = application.phone

    # --------------------------------------------------------
    # Avoid duplicate phone
    # --------------------------------------------------------

    if (
        phone_to_use
        and User.objects.filter(
            phone=phone_to_use
        ).exists()
    ):

        phone_to_use = None

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    user = User(
        full_name=application.full_name,
        email=application.email,
        phone=phone_to_use,
        role=application.role,
        is_verified=True,
        is_active=True,
        token_version=0,
    )

    # Password already hashed
    user.password = application.password

    user.save()

    # --------------------------------------------------------
    # Update application
    # --------------------------------------------------------

    application.status = "approved"
    application.reviewed_at = timezone.now()
    application.reviewed_by = reviewer

    application.save()

    # --------------------------------------------------------
    # Send confirmation email
    # --------------------------------------------------------

    send_registration_confirmation_email(
        user.email,
        user.full_name,
        user.role
    )

    return user


# ============================================================
# REJECT APPLICATION
# ============================================================

def _reject_application(
    application,
    reviewer
):
    """
    Shared rejection logic.
    """

    application.status = "rejected"
    application.reviewed_at = timezone.now()
    application.reviewed_by = reviewer

    application.save()

    send_mail(
        subject="Megeb+ Application Update",

        message=(
            f"Hi {application.full_name},\n\n"
            f"Thank you for applying to Megeb+ "
            f"as a {application.role}. "
            f"After review, we're unable to approve "
            f"your application at this time."
        ),

        from_email=settings.DEFAULT_FROM_EMAIL,

        recipient_list=[
            application.email
        ],

        fail_silently=False,
    )


# ============================================================
# APPROVE APPLICATION VIEW
# ============================================================

class ApproveApplicationView(APIView):

    permission_classes = [
        IsAdminRole
    ]

    def post(
        self,
        request,
        application_id
    ):

        application = StaffApplication.objects.filter(
            id=application_id,
            status="pending"
        ).first()

        if not application:

            return Response(
                {
                    "detail": (
                        "Application not found "
                        "or already reviewed."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        _approve_application(
            application,
            request.user
        )

        return Response(
            {
                "message": (
                    f"{application.role} approved "
                    "and account created."
                )
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# REJECT APPLICATION VIEW
# ============================================================

class RejectApplicationView(APIView):

    permission_classes = [
        IsAdminRole
    ]

    def post(
        self,
        request,
        application_id
    ):

        application = StaffApplication.objects.filter(
            id=application_id,
            status="pending"
        ).first()

        if not application:

            return Response(
                {
                    "detail": (
                        "Application not found "
                        "or already reviewed."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        _reject_application(
            application,
            request.user
        )

        return Response(
            {
                "message": (
                    "Application rejected "
                    "and applicant notified."
                )
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# CHANGE PASSWORD
# ============================================================

class ChangePasswordView(APIView):
    """
    Authenticated user changes password.
    Requires current password.
    """

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        serializer = ChangePasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user

        # ----------------------------------------------------
        # Verify current password
        # ----------------------------------------------------

        if not user.check_password(
            serializer.validated_data[
                "current_password"
            ]
        ):

            return Response(
                {
                    "detail": (
                        "Current password is incorrect."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Set new password
        # ----------------------------------------------------

        user.set_password(
            serializer.validated_data[
                "new_password"
            ]
        )

        # ----------------------------------------------------
        # Invalidate old tokens
        # ----------------------------------------------------

        user.token_version += 1

        user.save(
            update_fields=[
                "password",
                "token_version"
            ]
        )

        return Response(
            {
                "message": (
                    "Password changed successfully."
                )
            },
            status=status.HTTP_200_OK
        )