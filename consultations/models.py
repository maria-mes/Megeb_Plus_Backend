from django.db import models
from accounts.models import User


class AvailabilitySlot(models.Model):
    """A nutritionist-published open time slot. Users book against these."""

    nutritionist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="availability_slots",
        limit_choices_to={"role": "nutritionist"},
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.nutritionist} - {self.date} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """A user's booking against a specific AvailabilitySlot."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE, related_name="appointment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} -> {self.slot.nutritionist} ({self.status})"