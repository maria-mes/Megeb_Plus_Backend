from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    MeView,
    SendOTPView,
    VerifyOTPView,
    EmailRegisterView,
    SendEmailOTPView,
    VerifyEmailOTPView,
    ResetPasswordView,
    StaffApplyView,
    PendingApplicationsView,
    ApproveApplicationView,
    RejectApplicationView,
    ChangePasswordView,
)

urlpatterns = [
    # ---------------------------
    # Authentication
    # ---------------------------

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # ---------------------------
    # JWT
    # ---------------------------

    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),

    # ---------------------------
    # User
    # ---------------------------

    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    # ---------------------------
    # Phone OTP
    # ---------------------------

    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    # ---------------------------
    # Email registration / OTP
    # ---------------------------

    path("register-email/", EmailRegisterView.as_view(), name="register-email"),
    path("send-email-otp/", SendEmailOTPView.as_view(), name="send-email-otp"),
    path("verify-email-otp/", VerifyEmailOTPView.as_view(), name="verify-email-otp"),

    # ---------------------------
    # Password reset
    # ---------------------------

    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    # ---------------------------
    # Staff applications
    # ---------------------------

    path("apply-staff/", StaffApplyView.as_view(), name="apply-staff"),
    path(
        "applications/pending/",
        PendingApplicationsView.as_view(),
        name="pending-applications",
    ),
    path(
        "applications/<int:application_id>/approve/",
        ApproveApplicationView.as_view(),
        name="approve-application",
    ),
    path(
        "applications/<int:application_id>/reject/",
        RejectApplicationView.as_view(),
        name="reject-application",
    ),
    
]