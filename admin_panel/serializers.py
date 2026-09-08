from rest_framework import serializers
from accounts.models import User, StaffApplication
from appointments.models import Appointment
from health.models import Food
from .models import PlatformSettings
from vendors.models import VendorApplication


class AdminUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name")
    status = serializers.SerializerMethodField()
    joinedDate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "name", "email", "status", "joinedDate"]

    def get_status(self, obj):
        return "Active" if obj.is_active else "Suspended"

    def get_joinedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")


class AdminNutritionistSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name")
    specialty = serializers.SerializerMethodField()
    credentialType = serializers.SerializerMethodField()
    licenseNumber = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    appliedDate = serializers.SerializerMethodField()

    class Meta:
        model = StaffApplication
        fields = ["id", "name", "email", "specialty", "credentialType", "licenseNumber", "status", "appliedDate"]

    def get_specialty(self, obj):
        data = obj.application_data or {}
        return data.get("specialty") or data.get("specialization") or ""

    def get_credentialType(self, obj):
        data = obj.application_data or {}
        return data.get("credentialType") or data.get("credential_type") or data.get("degree") or ""

    def get_licenseNumber(self, obj):
        data = obj.application_data or {}
        return data.get("licenseNumber") or data.get("license_number") or ""

    def get_status(self, obj):
        return obj.status.capitalize()

    def get_appliedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")


class AdminAppointmentSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source="client.full_name")
    nutritionist = serializers.CharField(source="nutritionist.full_name")
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ["id", "client", "nutritionist", "date", "time", "status"]

    def get_date(self, obj):
        return obj.date.strftime("%Y-%m-%d")

    def get_time(self, obj):
        return obj.time.strftime("%I:%M %p").lstrip("0")

    def get_status(self, obj):
        # Frontend's AppointmentStatus type only has 3 states (no "completed"),
        # so completed appointments are shown as Confirmed for now.
        mapping = {
            "pending": "Pending",
            "confirmed": "Confirmed",
            "cancelled": "Cancelled",
            "completed": "Confirmed",
        }
        return mapping.get(obj.status, obj.status.capitalize())


class PlatformSettingsSerializer(serializers.ModelSerializer):
    platformName = serializers.CharField(source="platform_name")
    supportEmail = serializers.EmailField(source="support_email", required=False, allow_blank=True)
    maintenanceMode = serializers.BooleanField(source="maintenance_mode")
    emailNotifications = serializers.BooleanField(source="email_notifications")

    class Meta:
        model = PlatformSettings
        fields = ["platformName", "supportEmail", "maintenanceMode", "emailNotifications"]


class AdminFoodItemSerializer(serializers.ModelSerializer):
    """
    Maps health.models.Food (which stores nutrition per 100g, no
    serving-size concept) onto the admin Food Database page's flat
    FoodItem shape. `servingSize` is a fixed "100g" label rather than a
    fabricated value, since the underlying model has no such field.

    coerce_to_string=False on every decimal field: DRF serializes
    DecimalField as a JSON string by default ("170.00"), but the
    frontend's FoodItem type declares these as `number`.
    """

    calories = serializers.DecimalField(
        source="calories_per_100g", max_digits=7, decimal_places=2, coerce_to_string=False
    )
    protein = serializers.DecimalField(
        source="protein_g", max_digits=6, decimal_places=2, coerce_to_string=False
    )
    carbs = serializers.DecimalField(
        source="carbs_g", max_digits=6, decimal_places=2, coerce_to_string=False
    )
    fat = serializers.DecimalField(
        source="fat_g", max_digits=6, decimal_places=2, coerce_to_string=False
    )
    servingSize = serializers.SerializerMethodField()

    class Meta:
        model = Food
        fields = ["id", "name", "category", "calories", "protein", "carbs", "fat", "servingSize"]

    def get_servingSize(self, obj):
        return "100g"


class AdminProfileSerializer(serializers.ModelSerializer):
    """
    For the admin's own /admin/profile page. `role` is presented as the
    human label the frontend already shows ("System Administrator")
    rather than the raw "admin" choice value.
    """

    fullName = serializers.CharField(source="full_name")
    joinedDate = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["fullName", "email", "phone", "role", "joinedDate"]

    def get_joinedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    def get_role(self, obj):
        return "System Administrator" if obj.role == "admin" else obj.role.capitalize()
class AdminFoodVendorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    businessName = serializers.CharField(source="business_name")
    ownerName = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    businessLicenseNumber = serializers.CharField(
        source="license_number",
        allow_blank=True,
        required=False,
    )
    foodSafetyCertNumber = serializers.SerializerMethodField()
    address = serializers.CharField(source="business_address")
    status = serializers.SerializerMethodField()
    appliedDate = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = VendorApplication
        fields = [
            "id",
            "businessName",
            "ownerName",
            "email",
            "phone",
            "businessLicenseNumber",
            "foodSafetyCertNumber",
            "address",
            "status",
            "appliedDate",
            "documents",
        ]

    def get_foodSafetyCertNumber(self, obj):
        # VendorApplication currently stores the certificate as a file,
        # not as a separate certificate-number field.
        return ""

    def get_status(self, obj):
        return obj.status.capitalize()

    def get_appliedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    def get_documents(self, obj):
        request = self.context.get("request")
        documents = []

        files = [
            ("Business License", obj.license_document),
            ("Food Safety Certificate", obj.food_safety_certificate),
            ("Owner ID", obj.owner_id_document),
        ]

        for label, file_field in files:
            if not file_field:
                continue

            file_url = file_field.url
            if request:
                file_url = request.build_absolute_uri(file_url)

            filename = file_field.name.split("/")[-1]
            extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

            file_type = "image" if extension in {
                "jpg", "jpeg", "png", "webp", "gif"
            } else "pdf"

            documents.append({
                "label": label,
                "fileName": filename,
                "fileType": file_type,
                "fileUrl": file_url,
                "uploadedDate": obj.created_at.strftime("%Y-%m-%d"),
            })

        return documents