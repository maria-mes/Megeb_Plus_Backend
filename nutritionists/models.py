from django.conf import settings
from django.db import models


class NutritionistApplication(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    AI_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("failed", "Failed"),
        ("needs_review", "Needs Review"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nutritionist_application",
    )

    full_name = models.CharField(max_length=255)

    email = models.EmailField()

    phone = models.CharField(max_length=30)

    current_role = models.CharField(
        max_length=255,
        blank=True,
    )

    specialization = models.CharField(
        max_length=255,
    )

    qualification = models.CharField(
        max_length=255,
        blank=True,
    )

    years_of_experience = models.PositiveIntegerField(
        default=0,
    )

    license_number = models.CharField(
        max_length=255,
    )

    credential_document = models.FileField(
        upload_to="nutritionist_documents/",
        blank=True,
        null=True,
    )

    ai_status = models.CharField(
        max_length=30,
        choices=AI_STATUS_CHOICES,
        default="pending",
    )

    ai_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    ai_result = models.JSONField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    rejection_reason = models.TextField(
        blank=True,
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.full_name} - {self.license_number}"


class NutritionistProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nutritionist_profile",
    )

    bio = models.TextField(
        blank=True,
    )

    specialization = models.CharField(
        max_length=255,
        blank=True,
    )

    qualification = models.CharField(
        max_length=255,
        blank=True,
    )

    years_of_experience = models.PositiveIntegerField(
        default=0,
    )

    license_number = models.CharField(
        max_length=255,
        unique=True,
    )

    profile_picture = models.ImageField(
        upload_to="nutritionists/profile/",
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.user.full_name