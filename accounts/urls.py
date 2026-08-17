from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView, RegisterView, MeView, SendOTPView, VerifyOTPView,
    EmailRegisterView,
    SendEmailOTPView, VerifyEmailOTPView, ResetPasswordView,
    StaffApplyView, PendingApplicationsView, ApproveApplicationView, RejectApplicationView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("register-email/", EmailRegisterView.as_view(), name="register-email"),
    path("send-email-otp/", SendEmailOTPView.as_view(), name="send-email-otp"),
    path("verify-email-otp/", VerifyEmailOTPView.as_view(), name="verify-email-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),

    path("apply-staff/", StaffApplyView.as_view(), name="apply-staff"),
    path("applications/pending/", PendingApplicationsView.as_view(), name="pending-applications"),
    path("applications/<int:application_id>/approve/", ApproveApplicationView.as_view(), name="approve-application"),
    path("applications/<int:application_id>/reject/", RejectApplicationView.as_view(), name="reject-application"),
]