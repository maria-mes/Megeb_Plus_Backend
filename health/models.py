from django.db import models
from accounts.models import User


class HealthProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="health_profile"
    )

    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    activity_level = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    medical_conditions = models.JSONField(
        default=list,
        blank=True
    )

    allergies = models.JSONField(
        default=list,
        blank=True
    )

    dietary_preferences = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health Profile - {self.user.email}"
