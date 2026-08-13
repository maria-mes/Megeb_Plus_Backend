from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ForgotPasswordView,
    HealthProfileView,
    LoginView,
    MeView,
    RegisterView,
    ResendOTPView,
    ResetPasswordView,
    VerifyOTPView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("health-profile/", HealthProfileView.as_view(), name="health-profile"),
    path("me/", MeView.as_view(), name="me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]