from rest_framework import serializers

from django.contrib.auth import get_user_model
from .models import (
    NutritionistApplication,
    NutritionistProfile,
    ClientNote
)
from health.models import HealthProfile
from nutrition_plans.models import NutritionPlan
from appointments.models import Appointment
from django.contrib.auth import get_user_model
User = get_user_model()


class NutritionistApplicationSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = NutritionistApplication

        fields = [
            "id",
            "user",

            # Personal information
            "full_name",
            "email",
            "phone",

            # Professional information
            "current_role",
            "specialization",
            "years_of_experience",

            # State license
            "license_number",
            "license_jurisdiction",
            "license_expiration_date",
            "license_document",

            # National credential
            "credential_type",
            "credential_number",
            "credential_document",

            # Insurance
            "insurance_provider",
            "policy_number",
            "insurance_expiration_date",
            "coverage_limit",
            "insurance_document",

            # Degree
            "degree",
            "institution",
            "field_of_study",
            "graduation_year",
            "degree_document",

            # AI verification
            "ai_status",
            "ai_score",
            "ai_result",

            # Application status
            "status",
            "rejection_reason",
            "submitted_at",
            "reviewed_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",

            # AI fields are controlled by backend
            "ai_status",
            "ai_score",
            "ai_result",

            # Application status is controlled by backend/admin
            "status",
            "rejection_reason",
            "submitted_at",
            "reviewed_at",
            "updated_at",
        ]
class NutritionistProfileSerializer(
    serializers.ModelSerializer
):

    full_name = serializers.CharField(
        source="user.full_name",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = NutritionistProfile

        fields = [
            "id",
            "user",
            "full_name",
            "email",
            "bio",
            "specialization",
            "qualification",
            "years_of_experience",
            "license_number",
            "profile_picture",
            "is_verified",
            "rating",
            "consultation_fee",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "is_verified",
            "rating",
            "created_at",
            "updated_at",
        ]
from django.utils import timezone
from appointments.models import NutritionistAvailability


class NutritionistDirectorySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="user.full_name",
        read_only=True
    )
    user_id = serializers.IntegerField(
    source="user.id",
    read_only=True
    )
    currency = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    class Meta:
        model = NutritionistProfile
        fields = [
            "id",
            "user_id",
            "full_name",
            "specialization",
            "bio",
            "qualification",
            "years_of_experience",
            "consultation_fee",
            "currency",
            "rating",
            "profile_picture",
            "is_verified",
            "availability",
        ]

    def get_currency(self, obj):
        return "ETB"

    def get_availability(self, obj):
        today = timezone.localdate()

        day_of_week = today.weekday()

        has_availability = NutritionistAvailability.objects.filter(
            nutritionist=obj.user,
            day_of_week=day_of_week,
            is_active=True,
        ).exists()

        return "available" if has_availability else "unavailable"
class ClientNutritionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionPlan
        fields = [
            "id",
            "plan_name",
            "status",
            "start_date",
            "end_date",
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["id", "date", "time", "appointment_type", "mode", "status"]


class HealthProfileSerializer(serializers.ModelSerializer):
    height = serializers.DecimalField(
        source="height_cm", max_digits=5, decimal_places=2, required=False
    )
    weight = serializers.DecimalField(
        source="weight_kg", max_digits=5, decimal_places=2, required=False
    )

    class Meta:
        model = HealthProfile
        fields = [
            "age", "gender", "height", "weight",
            "activity_level", "medical_conditions",
            "health_goal", "diet_preference",
        ]


class ClientDetailSerializer(serializers.ModelSerializer):

    # ---------------------------------------
    # HEALTH PROFILE FIELDS
    # ---------------------------------------

    age = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()
    currentWeight = serializers.SerializerMethodField()
    targetWeight = serializers.SerializerMethodField()
    bmi = serializers.SerializerMethodField()
    goal = serializers.SerializerMethodField()
    medicalCondition = serializers.SerializerMethodField()
    activityLevel = serializers.SerializerMethodField()

    # ---------------------------------------
    # EXISTING FIELDS
    # ---------------------------------------

    preferences = serializers.SerializerMethodField()
    allergies = serializers.SerializerMethodField()
    nutrition_plans = serializers.SerializerMethodField()

    # ---------------------------------------
    # APPOINTMENTS
    # ---------------------------------------

    appointments = AppointmentSerializer(
        many=True,
        source="client_appointments",
        read_only=True
    )

    # ---------------------------------------
    # PROGRESS
    # ---------------------------------------

    progress = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "profile_picture",
            "is_verified",

            # Health information
            "age",
            "gender",
            "height",
            "currentWeight",
            "targetWeight",
            "bmi",
            "goal",
            "medicalCondition",
            "activityLevel",

            # Existing information
            "preferences",
            "allergies",
            "nutrition_plans",

            # Appointments
            "appointments",

            # Progress
            "progress",
        ]

    # =======================================
    # HEALTH PROFILE
    # =======================================

    def get_health_profile(self, obj):
        try:
            return obj.health_profile
        except HealthProfile.DoesNotExist:
            return None

    def get_age(self, obj):
        profile = self.get_health_profile(obj)
        return profile.age if profile else None

    def get_gender(self, obj):
        profile = self.get_health_profile(obj)
        return profile.gender if profile else None

    def get_height(self, obj):
        profile = self.get_health_profile(obj)
        return float(profile.height_cm) if profile and profile.height_cm is not None else None

    def get_currentWeight(self, obj):
        profile = self.get_health_profile(obj)
        return float(profile.weight_kg) if profile and profile.weight_kg is not None else None

    def get_targetWeight(self, obj):
        """
        Target weight is NOT stored in HealthProfile.

        It should come from NutritionGoal.target_weight_kg.

        This is temporarily returning None until the exact
        NutritionGoal relationship/model is confirmed.
        """
        return None

    def get_bmi(self, obj):
        profile = self.get_health_profile(obj)

        if not profile:
            return None

        if profile.height_cm is None or profile.weight_kg is None:
            return None

        height_m = float(profile.height_cm) / 100
        weight_kg = float(profile.weight_kg)

        if height_m <= 0:
            return None

        bmi = weight_kg / (height_m ** 2)

        return round(bmi, 2)

    def get_goal(self, obj):
        profile = self.get_health_profile(obj)
        return profile.health_goal if profile else None

    def get_medicalCondition(self, obj):
        profile = self.get_health_profile(obj)

        if not profile or not profile.medical_conditions:
            return []

        return profile.medical_conditions

    def get_activityLevel(self, obj):
        profile = self.get_health_profile(obj)
        return profile.activity_level if profile else None

    # =======================================
    # PREFERENCES
    # =======================================

    def get_preferences(self, obj):
        profile = self.get_health_profile(obj)

        if not profile or not profile.diet_preference:
            return []

        return [profile.diet_preference]

    # =======================================
    # ALLERGIES
    # =======================================

    def get_allergies(self, obj):
        profile = self.get_health_profile(obj)

        if not profile or not profile.allergies:
            return []

        return profile.allergies

    # =======================================
    # NUTRITION PLANS
    # =======================================

    def get_nutrition_plans(self, obj):
        nutritionist = self.context["request"].user

        plans = obj.nutrition_plans.filter(
            nutritionist=nutritionist
        ).order_by("-created_at")

        return ClientNutritionPlanSerializer(
            plans,
            many=True
        ).data

    # =======================================
    # PROGRESS
    # =======================================

    def get_progress(self, obj):
        profile = self.get_health_profile(obj)

        current_weight = None

        if profile and profile.weight_kg is not None:
            current_weight = float(profile.weight_kg)

        return {
            "currentWeight": current_weight,
            "weightHistory": [],
            "caloriesConsumed": 0,
            "calorieGoal": 0,
            "activityBurned": 0,
            "waterConsumed": 0,
            "waterGoal": 0,
        }


class ClientNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientNote
        fields = [
            "id",
            "nutritionist",
            "client",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "nutritionist",
            "client",
            "created_at",
            "updated_at",
        ]
