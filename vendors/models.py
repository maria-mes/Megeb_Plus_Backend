from django.conf import settings
from django.db import models


class VendorApplication(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    AI_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("needs_review", "Needs Review"),
        ("failed", "Failed"),
    ]

    BUSINESS_TYPE_CHOICES = [
        ("restaurant", "Restaurant"),
        ("catering", "Catering Service"),
        ("food_manufacturer", "Food Manufacturer"),
        ("grocery", "Grocery / Food Store"),
        ("bakery", "Bakery"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_application",
    )

    business_name = models.CharField(max_length=255)

    business_address = models.TextField()

    business_type = models.CharField(
        max_length=50,
        choices=BUSINESS_TYPE_CHOICES,
    )

    license_number = models.CharField(
        max_length=100,
        unique=True,
    )

    license_document = models.FileField(
        upload_to="vendors/licenses/",
    )

    food_safety_certificate = models.FileField(
        upload_to="vendors/food_safety/",
    )

    owner_id_document = models.FileField(
        upload_to="vendors/owner_ids/",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    ai_status = models.CharField(
        max_length=20,
        choices=AI_STATUS_CHOICES,
        default="pending",
    )

    ai_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    ai_result = models.JSONField(
        default=dict,
        blank=True,
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.business_name} - {self.status}"


class VendorProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
    )

    business_name = models.CharField(max_length=255)

    business_address = models.TextField()

    business_type = models.CharField(max_length=50)

    is_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name


class VendorProduct(models.Model):

    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name="products",
    )

    name = models.CharField(max_length=255)

    description = models.TextField(
        blank=True,
        null=True,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    category = models.CharField(max_length=100)

    photo = models.ImageField(
        upload_to="vendors/products/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"