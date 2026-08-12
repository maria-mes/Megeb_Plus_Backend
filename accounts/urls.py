from django.urls import path
from .views import LoginView, RegisterView , MeView , SendOTPView, VerifyOTPView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path(
        "send-otp/",
        SendOTPView.as_view(),
        name="send-otp"
    ),
    path(
        "verify-otp/",
        VerifyOTPView.as_view(),
        name="verify-otp"
    ),

    path(
    "token/refresh/",
    TokenRefreshView.as_view(),
    name="token_refresh"
),
]