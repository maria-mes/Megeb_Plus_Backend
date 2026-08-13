from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("user", "User"),
        ("nutritionist", "Nutritionist"),
        ("admin", "Admin"),
        ("vendor", "Vendor"),
    ]

    id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=False, blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    profile_picture = models.URLField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone or self.email or str(self.id)


class PhoneOTP(models.Model):
    PURPOSE_REGISTER = "register"
    PURPOSE_RESET_PASSWORD = "reset_password"

    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, "Register"),
        (PURPOSE_RESET_PASSWORD, "Reset Password"),
    ]

    phone = models.CharField(max_length=20)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default=PURPOSE_REGISTER)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    def is_valid(self, now=None):
        from django.utils import timezone

        if now is None:
            now = timezone.now()
        return not self.is_used and now < self.expires_at