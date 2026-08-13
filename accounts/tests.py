from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import PhoneOTP, User


class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_sends_otp_and_creates_inactive_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "full_name": "Test User",
                "phone": "+251911000000",
                "password": "Pass1234",
                "confirm_password": "Pass1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(phone="+251911000000").exists())
        user = User.objects.get(phone="+251911000000")
        self.assertFalse(user.is_active)
        self.assertTrue(PhoneOTP.objects.filter(phone="+251911000000").exists())

    def test_verify_otp_activates_user(self):
        user = User.objects.create_user(
            phone="+251911000001",
            password="Pass1234",
            full_name="Another User",
            is_active=False,
            is_verified=False,
        )

        otp = PhoneOTP.objects.create(
            phone=user.phone,
            otp_code="123456",
            purpose=PhoneOTP.PURPOSE_REGISTER,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        response = self.client.post(
            reverse("verify-otp"),
            {"phone": user.phone, "otp": otp.otp_code, "purpose": PhoneOTP.PURPOSE_REGISTER},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_verified)
