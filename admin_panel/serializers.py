from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from accounts.models import User, StaffApplication
from appointments.models import Appointment
from health.models import Food, WeightLog
from vendors.models import VendorApplication

from .models import PlatformSettings


# ============================================================
# USERS
# ============================================================

class AdminUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name", read_only=True)
    status = serializers.SerializerMethodField()
    joinedDate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "name", "email", "status", "joinedDate"]

    def get_status(self, obj):
        return "Active" if obj.is_active else "Suspended"

    def get_joinedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")


# ============================================================
# CLIENT APPOINTMENTS
# ============================================================

class AdminClientAppointmentSerializer(serializers.ModelSerializer):
    nutritionist = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ["id", "nutritionist", "date", "time", "status"]

    def get_nutritionist(self, obj):
        if not obj.nutritionist:
            return None
        return obj.nutritionist.full_name

    def get_date(self, obj):
        if not obj.date:
            return ""
        return obj.date.strftime("%Y-%m-%d")

    def get_time(self, obj):
        if not obj.time:
            return ""
        return obj.time.strftime("%I:%M %p").lstrip("0")

    def get_status(self, obj):
        mapping = {
            "pending": "Pending",
            "confirmed": "Confirmed",
            "cancelled": "Cancelled",
            "completed": "Completed",
        }
        return mapping.get(obj.status, obj.status.capitalize())


# ============================================================
# CLIENT LIST SERIALIZER
# ============================================================

class AdminClientListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name", read_only=True)
    age = serializers.SerializerMethodField()
    assignedNutritionist = serializers.SerializerMethodField()
    nextAppointment = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "name", "age", "assignedNutritionist",
            "nextAppointment", "status",
        ]

    def _profile(self, obj):
        return getattr(obj, "health_profile", None)

    def _upcoming_appointment(self, obj):
        appointments = getattr(obj, "client_appointments", None)
        if appointments is None:
            return None
        today = timezone.localdate()
        return (
            appointments
            .filter(date__gte=today, status__in=["pending", "confirmed"])
            .select_related("nutritionist")
            .order_by("date", "time")
            .first()
        )

    def get_age(self, obj):
        profile = self._profile(obj)
        if not profile:
            return None
        return profile.age

    def get_assignedNutritionist(self, obj):
        appointment = self._upcoming_appointment(obj)
        if appointment and appointment.nutritionist:
            return appointment.nutritionist.full_name
        return None

    def get_nextAppointment(self, obj):
        appointment = self._upcoming_appointment(obj)
        if not appointment:
            return "Not scheduled"
        today = timezone.localdate()
        if appointment.date == today:
            day_text = "Today"
        elif appointment.date == today + timedelta(days=1):
            day_text = "Tomorrow"
        else:
            day_text = (
                f"{appointment.date.strftime('%b')} "
                f"{appointment.date.strftime('%d').lstrip('0')}"
            )
        time_text = appointment.time.strftime("%I:%M %p").lstrip("0")
        return f"{day_text}, {time_text}"

    def get_status(self, obj):
        return "Active" if obj.is_active else "Suspended"


# ============================================================
# CLIENT DETAIL SERIALIZER
# ============================================================

class AdminClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name", read_only=True)
    age = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    joinedDate = serializers.SerializerMethodField()

    height = serializers.SerializerMethodField()
    currentWeight = serializers.SerializerMethodField()
    targetWeight = serializers.SerializerMethodField()
    bmi = serializers.SerializerMethodField()

    goal = serializers.SerializerMethodField()
    goalDescription = serializers.SerializerMethodField()

    medicalCondition = serializers.SerializerMethodField()
    activityLevel = serializers.SerializerMethodField()
    allergies = serializers.SerializerMethodField()

    assignedNutritionist = serializers.SerializerMethodField()
    nutritionPlan = serializers.SerializerMethodField()
    calories = serializers.SerializerMethodField()
    dietType = serializers.SerializerMethodField()

    progress = serializers.SerializerMethodField()

    nextAppointment = serializers.SerializerMethodField()
    appointments = serializers.SerializerMethodField()

    nutritionistNotes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "name", "age", "gender", "phone", "email", "status",
            "joinedDate", "assignedNutritionist", "height", "currentWeight",
            "targetWeight", "bmi", "goal", "goalDescription",
            "medicalCondition", "activityLevel", "allergies",
            "nutritionPlan", "calories", "dietType", "progress",
            "nextAppointment", "appointments", "nutritionistNotes",
        ]

    def _profile(self, obj):
        return getattr(obj, "health_profile", None)

    def _goals(self, obj):
        manager = getattr(obj, "nutrition_goals", None)
        if manager is None:
            return []
        return list(manager.order_by("-created_at"))

    def _latest_goal(self, obj):
        goals = self._goals(obj)
        if not goals:
            return None
        active_goals = [g for g in goals if g.status == "active"]
        return active_goals[0] if active_goals else goals[0]

    def _plans(self, obj):
        manager = getattr(obj, "nutrition_plans", None)
        if manager is None:
            return []
        return list(manager.order_by("-created_at"))

    def _latest_plan(self, obj):
        plans = self._plans(obj)
        if not plans:
            return None
        active_plans = [p for p in plans if p.status == "Active"]
        return active_plans[0] if active_plans else plans[0]

    def _appointments(self, obj):
        manager = getattr(obj, "client_appointments", None)
        if manager is None:
            return []
        return list(manager.select_related("nutritionist", "consultation"))

    def _upcoming_appointment(self, obj):
        appointments = self._appointments(obj)
        today = timezone.localdate()
        upcoming = [
            a for a in appointments
            if a.date and a.date >= today and a.status in ["pending", "confirmed"]
        ]
        upcoming.sort(key=lambda a: (a.date, a.time))
        return upcoming[0] if upcoming else None

    def get_age(self, obj):
        profile = self._profile(obj)
        return profile.age if profile else None

    def get_gender(self, obj):
        profile = self._profile(obj)
        if not profile or not profile.gender:
            return ""
        return profile.get_gender_display()

    def get_status(self, obj):
        return "Active" if obj.is_active else "Suspended"

    def get_joinedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    def get_height(self, obj):
        profile = self._profile(obj)
        if not profile or profile.height_cm is None:
            return ""
        return f"{profile.height_cm} cm"

    def get_currentWeight(self, obj):
        profile = self._profile(obj)
        if profile and profile.weight_kg is not None:
            return f"{profile.weight_kg} kg"
        logs = list(WeightLog.objects.filter(user=obj).order_by("-date"))
        if logs:
            return f"{logs[0].weight_kg} kg"
        return ""

    def get_targetWeight(self, obj):
        goal = self._latest_goal(obj)
        if goal and goal.target_weight_kg is not None:
            return f"{goal.target_weight_kg} kg"
        return ""

    def get_bmi(self, obj):
        profile = self._profile(obj)
        if not profile or profile.height_cm is None or profile.weight_kg is None:
            return ""
        if profile.height_cm <= 0:
            return ""
        height_m = float(profile.height_cm) / 100
        bmi = float(profile.weight_kg) / (height_m ** 2)
        return f"{bmi:.1f}"

    def get_goal(self, obj):
        profile = self._profile(obj)
        if not profile or not profile.health_goal:
            return ""
        return profile.get_health_goal_display()

    def get_goalDescription(self, obj):
        profile = self._profile(obj)
        if not profile:
            return ""
        if profile.other_health_goal:
            return profile.other_health_goal
        if profile.health_goal:
            return profile.get_health_goal_display()
        return ""

    def get_medicalCondition(self, obj):
        profile = self._profile(obj)
        if not profile or not profile.medical_conditions:
            return ""
        conditions = profile.medical_conditions
        if isinstance(conditions, list):
            return ", ".join(str(c) for c in conditions)
        return str(conditions)

    def get_activityLevel(self, obj):
        profile = self._profile(obj)
        if not profile or not profile.activity_level:
            return ""
        return profile.get_activity_level_display()

    def get_allergies(self, obj):
        profile = self._profile(obj)
        if not profile:
            return ""
        values = []
        allergies = profile.allergies or []
        if isinstance(allergies, list):
            values.extend(str(a) for a in allergies)
        else:
            values.append(str(allergies))
        if profile.other_allergy:
            values.append(profile.other_allergy)
        return ", ".join(values)

    def get_assignedNutritionist(self, obj):
        appointment = self._upcoming_appointment(obj)
        if appointment and appointment.nutritionist:
            return appointment.nutritionist.full_name
        plan = self._latest_plan(obj)
        if plan and plan.nutritionist:
            return plan.nutritionist.full_name
        return None

    def get_nutritionPlan(self, obj):
        plan = self._latest_plan(obj)
        return plan.plan_name if plan else ""

    def get_calories(self, obj):
        plan = self._latest_plan(obj)
        if plan and plan.target_calories is not None:
            return f"{plan.target_calories} kcal/day"
        profile = self._profile(obj)
        if profile and profile.calorie_target is not None:
            return f"{profile.calorie_target} kcal/day"
        return ""

    def get_dietType(self, obj):
        profile = self._profile(obj)
        if not profile or not profile.diet_preference:
            return []
        return [profile.get_diet_preference_display()]

    def get_progress(self, obj):
        logs = list(WeightLog.objects.filter(user=obj).order_by("date"))
        profile = self._profile(obj)
        starting_weight = None
        current_weight = None
        if logs:
            starting_weight = logs[0].weight_kg
        if profile and profile.weight_kg is not None:
            current_weight = profile.weight_kg
        elif logs:
            current_weight = logs[-1].weight_kg
        if starting_weight is None:
            starting_weight = current_weight
        if starting_weight is None or current_weight is None:
            return {"startingWeight": "", "currentWeight": "", "weightLost": ""}
        weight_lost = float(starting_weight) - float(current_weight)
        return {
            "startingWeight": f"{starting_weight} kg",
            "currentWeight": f"{current_weight} kg",
            "weightLost": f"{weight_lost:.1f} kg",
        }

    def get_nextAppointment(self, obj):
        appointment = self._upcoming_appointment(obj)
        if not appointment:
            return None
        return {
            "date": appointment.date.strftime("%Y-%m-%d"),
            "time": appointment.time.strftime("%I:%M %p").lstrip("0"),
        }

    def get_appointments(self, obj):
        appointments = self._appointments(obj)
        appointments.sort(key=lambda a: (a.date, a.time), reverse=True)
        return AdminClientAppointmentSerializer(appointments, many=True).data

    def get_nutritionistNotes(self, obj):
        appointments = self._appointments(obj)
        appointments.sort(key=lambda a: (a.date, a.time), reverse=True)
        for appointment in appointments:
            consultation = getattr(appointment, "consultation", None)
            if consultation and consultation.nutritionist_notes:
                return consultation.nutritionist_notes
        return ""


# ============================================================
# NUTRITIONISTS
# ============================================================

class AdminNutritionistSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name", read_only=True)
    specialty = serializers.CharField(source="specialization", read_only=True)
    credentialType = serializers.CharField(source="credential_type", read_only=True)
    licenseNumber = serializers.CharField(source="license_number", read_only=True)
    status = serializers.SerializerMethodField()
    appliedDate = serializers.SerializerMethodField()

    class Meta:
        model = StaffApplication
        fields = [
            "id", "name", "email", "specialty", "credentialType",
            "licenseNumber", "status", "appliedDate",
        ]

    def get_status(self, obj):
        return obj.status.capitalize()

    def get_appliedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")


# ============================================================
# APPOINTMENTS
# ============================================================

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
        if not obj.date:
            return ""
        return obj.date.strftime("%Y-%m-%d")

    def get_time(self, obj):
        if not obj.time:
            return ""
        return obj.time.strftime("%I:%M %p").lstrip("0")

    def get_status(self, obj):
        mapping = {
            "pending": "Pending",
            "confirmed": "Confirmed",
            "cancelled": "Cancelled",
            "completed": "Confirmed",
        }
        return mapping.get(obj.status, obj.status.capitalize())


# ============================================================
# PLATFORM SETTINGS
# ============================================================

class PlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSettings
        fields = "__all__"


# ============================================================
# FOOD ITEMS
# ============================================================

class AdminFoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = "__all__"


# ============================================================
# ADMIN PROFILE
# ============================================================

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "phone", "role", "is_active"]
        read_only_fields = ["id", "role", "is_active"]


# ============================================================
# FOOD VENDORS
#
# FIX: rewritten from `fields = "__all__"` (which only pulled
# columns that live directly on VendorApplication, silently
# dropping email/phone which live on the related User) to an
# explicit serializer that outputs exactly the shape
# app/(admin)/food-vendors/page.tsx expects: camelCase field
# names, capitalized status, and a documents[] array.
#
# NOTE: I don't have DocumentPreviewModal / the SubmittedDocument
# type, so `documents` below assumes {label, fileName, fileUrl}.
# If the modal expects different keys, tell me and I'll adjust.
# ============================================================

class AdminFoodVendorSerializer(serializers.ModelSerializer):

    businessName = serializers.CharField(
        source="business_name", read_only=True
    )

    ownerName = serializers.CharField(
        source="user.full_name", read_only=True
    )

    email = serializers.EmailField(
        source="user.email", read_only=True
    )

    phone = serializers.CharField(
        source="user.phone", read_only=True
    )

    address = serializers.CharField(
        source="business_address", read_only=True
    )

    businessLicenseNumber = serializers.CharField(
        source="license_number", read_only=True
    )

    # NOTE: VendorApplication has no separate "food safety
    # certificate number" field, only the uploaded file.
    # Falling back to license_number would be wrong, so this
    # returns the file name for now — add a real field on the
    # model if you need a distinct certificate number.
    foodSafetyCertNumber = serializers.SerializerMethodField()

    appliedDate = serializers.SerializerMethodField()

    status = serializers.CharField(
        source="get_status_display", read_only=True
    )

    documents = serializers.SerializerMethodField()

    class Meta:
        model = VendorApplication
        fields = [
            "id",
            "businessName",
            "ownerName",
            "email",
            "phone",
            "address",
            "businessLicenseNumber",
            "foodSafetyCertNumber",
            "appliedDate",
            "status",
            "documents",
            "ai_status",
            "ai_score",
            "rejection_reason",
        ]

    def get_foodSafetyCertNumber(self, obj):
        if not obj.food_safety_certificate:
            return ""
        return obj.food_safety_certificate.name.rsplit("/", 1)[-1]

    def get_appliedDate(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")

    def _file_url(self, request, field_file):
        if not field_file:
            return None
        if request:
            return request.build_absolute_uri(field_file.url)
        return field_file.url

    def get_documents(self, obj):
        request = self.context.get("request")

        docs = []

        if obj.license_document:
            docs.append({
                "label": "Business License",
                "fileName": obj.license_document.name.rsplit("/", 1)[-1],
                "fileUrl": self._file_url(request, obj.license_document),
            })

        if obj.food_safety_certificate:
            docs.append({
                "label": "Food Safety Certificate",
                "fileName": obj.food_safety_certificate.name.rsplit("/", 1)[-1],
                "fileUrl": self._file_url(request, obj.food_safety_certificate),
            })

        if obj.owner_id_document:
            docs.append({
                "label": "Owner ID",
                "fileName": obj.owner_id_document.name.rsplit("/", 1)[-1],
                "fileUrl": self._file_url(request, obj.owner_id_document),
            })

        return docs