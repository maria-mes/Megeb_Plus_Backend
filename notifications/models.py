from django.conf import settings
from django.db import models


class Notification(models.Model):

    TYPE_CHOICES = [
        ("appointment", "Appointment"),
        ("message", "Message"),
        ("plan", "Plan"),
    ]

    id = models.BigAutoField(primary_key=True)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.full_name} - {self.title}"