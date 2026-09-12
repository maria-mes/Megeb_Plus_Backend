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

        return mapping.get(
            obj.status,
            obj.status.capitalize(),
        )


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
            "id",
            "name",
            "age",
            "assignedNutritionist",
            "nextAppointment",
            "status",
        ]

    def _profile(self, obj):
        return getattr(obj, "health_profile", None)

    def _upcoming_appointment(self, obj):
        appointments = getattr(
            obj,
            "client_appointments",
            None,
        )

        if appointments is None:
            return None

        today = timezone.localdate()

        return (
            appointments
            .filter(
                date__gte=today,
                status__in=["pending", "confirmed"],
            )
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

        time_text = appointment.time.strftime(
            "%I:%M %p"
        ).lstrip("0")

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
            "id",
            "name",
            "age",
            "gender",
            "phone",
            "email",
            "status",
            "joinedDate",
            "assignedNutritionist",
            "height",
            "currentWeight",
            "targetWeight",
            "bmi",
            "goal",
            "goalDescription",
            "medicalCondition",
            "activityLevel",
            "allergies",
            "nutritionPlan",
            "calories",
            "dietType",
            "progress",
            "nextAppointment",
            "appointments",
            "nutritionistNotes",
        ]

    def _profile(self, obj):
        return getattr(obj, "health_profile", None)

    def _goals(self, obj):
        manager = getattr(
            obj,
            "nutrition_goals",
            None,
        )

        if manager is None:
            return []

        return list(
            manager.order_by("-created_at")
        )

    def _latest_goal(self, obj):
        goals = self._goals(obj)

        if not goals:
            return None

        active_goals = [
            g
            for g in goals
            if g.status == "active"
        ]

        return (
            active_goals[0]
            if active_goals
            else goals[0]
        )

    def _plans(self, obj):
        manager = getattr(
            obj,
            "nutrition_plans",
            None,
        )

        if manager is None:
            return []

        return list(
            manager.order_by("-created_at")
        )

    def _latest_plan(self, obj):
        plans = self._plans(obj)

        if not plans:
            return None

        active_plans = [
            p
            for p in plans
            if p.status == "Active"
        ]

        return (
            active_plans[0]
            if active_plans
            else plans[0]
        )

    def _appointments(self, obj):
        manager = getattr(
            obj,
            "client_appointments",
            None,
        )

        if manager is None:
            return []

        return list(
            manager.select_related(
                "nutritionist",
                "consultation",
            )
        )

    def _upcoming_appointment(self, obj):
        appointments = self._appointments(obj)
        today = timezone.localdate()

        upcoming = [
            a
            for a in appointments
            if (
                a.date
                and a.date >= today
                and a.status in [
                    "pending",
                    "confirmed",
                ]
            )
        ]

        upcoming.sort(
            key=lambda a: (
                a.date,
                a.time,
            )
        )

        return (
            upcoming[0]
            if upcoming
            else None
        )

    def get_age(self, obj):
        profile = self._profile(obj)

        return (
            profile.age
            if profile
            else None
        )

    def get_gender(self, obj):
        profile = self._profile(obj)

        if not profile or not profile.gender:
            return ""

        return profile.get_gender_display()

    def get_status(self, obj):
        return (
            "Active"
            if obj.is_active
            else "Suspended"
        )

    def get_joinedDate(self, obj):
        return obj.created_at.strftime(
            "%Y-%m-%d"
        )

    def get_height(self, obj):
        profile = self._profile(obj)

        if (
            not profile
            or profile.height_cm is None
        ):
            return ""

        return f"{profile.height_cm} cm"

    def get_currentWeight(self, obj):
        profile = self._profile(obj)

        if (
            profile
            and profile.weight_kg is not None
        ):
            return f"{profile.weight_kg} kg"

        logs = list(
            WeightLog.objects
            .filter(user=obj)
            .order_by("-date")
        )

        if logs:
            return f"{logs[0].weight_kg} kg"

        return ""

    def get_targetWeight(self, obj):
        goal = self._latest_goal(obj)

        if (
            goal
            and goal.target_weight_kg is not None
        ):
            return f"{goal.target_weight_kg} kg"

        return ""

    def get_bmi(self, obj):
        profile = self._profile(obj)

        if (
            not profile
            or profile.height_cm is None
            or profile.weight_kg is None
        ):
            return ""

        if profile.height_cm <= 0:
            return ""

        height_m = float(
            profile.height_cm
        ) / 100

        bmi = float(
            profile.weight_kg
        ) / (height_m ** 2)

        return f"{bmi:.1f}"

    def get_goal(self, obj):
        profile = self._profile(obj)

        if (
            not profile
            or not profile.health_goal
        ):
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

        if (
            not profile
            or not profile.medical_conditions
        ):
            return ""

        conditions = profile.medical_conditions

        if isinstance(
            conditions,
            list,
        ):
            return ", ".join(
                str(c)
                for c in conditions
            )

        return str(conditions)

    def get_activityLevel(self, obj):
        profile = self._profile(obj)

        if (
            not profile
            or not profile.activity_level
        ):
            return ""

        return profile.get_activity_level_display()

    def get_allergies(self, obj):
        profile = self._profile(obj)

        if not profile:
            return ""

        values = []

        allergies = profile.allergies or []

        if isinstance(
            allergies,
            list,
        ):
            values.extend(
                str(a)
                for a in allergies
            )
        else:
            values.append(
                str(allergies)
            )

        if profile.other_allergy:
            values.append(
                profile.other_allergy
            )

        return ", ".join(values)

    def get_assignedNutritionist(self, obj):
        appointment = self._upcoming_appointment(obj)

        if (
            appointment
            and appointment.nutritionist
        ):
            return (
                appointment.nutritionist.full_name
            )

        plan = self._latest_plan(obj)

        if (
            plan
            and plan.nutritionist
        ):
            return (
                plan.nutritionist.full_name
            )

        return None

    def get_nutritionPlan(self, obj):
        plan = self._latest_plan(obj)

        return (
            plan.plan_name
            if plan
            else ""
        )

    def get_calories(self, obj):
        plan = self._latest_plan(obj)

        if (
            plan
            and plan.target_calories is not None
        ):
            return (
                f"{plan.target_calories} kcal/day"
            )

        profile = self._profile(obj)

        if (
            profile
            and profile.calorie_target is not None
        ):
            return (
                f"{profile.calorie_target} kcal/day"
            )

        return ""

    def get_dietType(self, obj):
        profile = self._profile(obj)

        if (
            not profile
            or not profile.diet_preference
        ):
            return []

        return [
            profile.get_diet_preference_display()
        ]

    def get_progress(self, obj):
        logs = list(
            WeightLog.objects
            .filter(user=obj)
            .order_by("date")
        )

        profile = self._profile(obj)

        starting_weight = None
        current_weight = None

        if logs:
            starting_weight = logs[0].weight_kg

        if (
            profile
            and profile.weight_kg is not None
        ):
            current_weight = profile.weight_kg

        elif logs:
            current_weight = logs[-1].weight_kg

        if starting_weight is None:
            starting_weight = current_weight

        if (
            starting_weight is None
            or current_weight is None
        ):
            return {
                "startingWeight": "",
                "currentWeight": "",
                "weightLost": "",
            }

        weight_lost = (
            float(starting_weight)
            - float(current_weight)
        )

        return {
            "startingWeight": (
                f"{starting_weight} kg"
            ),
            "currentWeight": (
                f"{current_weight} kg"
            ),
            "weightLost": (
                f"{weight_lost:.1f} kg"
            ),
        }

    def get_nextAppointment(self, obj):
        appointment = self._upcoming_appointment(obj)

        if not appointment:
            return None

        return {
            "date": appointment.date.strftime(
                "%Y-%m-%d"
            ),
            "time": appointment.time.strftime(
                "%I:%M %p"
            ).lstrip("0"),
        }

    def get_appointments(self, obj):
        appointments = self._appointments(obj)

        appointments.sort(
            key=lambda a: (
                a.date,
                a.time,
            ),
            reverse=True,
        )

        return AdminClientAppointmentSerializer(
            appointments,
            many=True,
        ).data

    def get_nutritionistNotes(self, obj):
        appointments = self._appointments(obj)

        appointments.sort(
            key=lambda a: (
                a.date,
                a.time,
            ),
            reverse=True,
        )

        for appointment in appointments:
            consultation = getattr(
                appointment,
                "consultation",
                None,
            )

            if (
                consultation
                and consultation.nutritionist_notes
            ):
                return (
                    consultation.nutritionist_notes
                )

        return ""


# ============================================================
# NUTRITIONISTS
# ============================================================

class AdminNutritionistSerializer(serializers.ModelSerializer):
    """
    Serializer for nutritionist staff applications.

    Converts the StaffApplication database fields into the
    camelCase structure expected by the admin frontend.
    """

    id = serializers.IntegerField(
        read_only=True
    )

    fullName = serializers.CharField(
        source="full_name",
        read_only=True
    )

    name = serializers.CharField(
        source="full_name",
        read_only=True
    )

    email = serializers.EmailField(
        read_only=True
    )

    phone = serializers.CharField(
        read_only=True,
        allow_null=True
    )

    currentRole = serializers.CharField(
        source="current_role",
        read_only=True
    )

    specialty = serializers.CharField(
        source="specialization",
        read_only=True
    )

    specialization = serializers.CharField(
        read_only=True
    )

    yearsOfExperience = serializers.IntegerField(
        source="years_of_experience",
        read_only=True,
        allow_null=True
    )

    licenseNumber = serializers.CharField(
        source="license_number",
        read_only=True
    )

    licenseState = serializers.CharField(
        source="license_jurisdiction",
        read_only=True
    )

    licenseExpiration = serializers.DateField(
        source="license_expiration_date",
        read_only=True,
        allow_null=True
    )

    credentialType = serializers.CharField(
        source="credential_type",
        read_only=True
    )

    credentialNumber = serializers.CharField(
        source="credential_number",
        read_only=True
    )

    insuranceProvider = serializers.CharField(
        source="insurance_provider",
        read_only=True
    )

    policyNumber = serializers.CharField(
        source="policy_number",
        read_only=True
    )

    insuranceExpiration = serializers.DateField(
        source="insurance_expiration_date",
        read_only=True,
        allow_null=True
    )

    coverageLimit = serializers.DecimalField(
        source="coverage_limit",
        max_digits=15,
        decimal_places=2,
        read_only=True,
        allow_null=True
    )

    degree = serializers.CharField(
        read_only=True
    )

    institution = serializers.CharField(
        read_only=True
    )

    fieldOfStudy = serializers.CharField(
        source="field_of_study",
        read_only=True
    )

    graduationYear = serializers.IntegerField(
        source="graduation_year",
        read_only=True,
        allow_null=True
    )

    submitted = serializers.SerializerMethodField()

    appliedDate = serializers.SerializerMethodField()

    status = serializers.SerializerMethodField()

    rejectionReason = serializers.CharField(
        source="rejection_reason",
        read_only=True,
        allow_null=True
    )

    documents = serializers.SerializerMethodField()

    aiStatus = serializers.CharField(
        source="ai_status",
        read_only=True
    )

    aiScore = serializers.DecimalField(
        source="ai_score",
        max_digits=5,
        decimal_places=2,
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = StaffApplication

        fields = [
            "id",

            # Basic information
            "fullName",
            "name",
            "email",
            "phone",

            # Professional information
            "currentRole",
            "specialty",
            "specialization",
            "yearsOfExperience",

            # License
            "licenseNumber",
            "licenseState",
            "licenseExpiration",

            # Credential
            "credentialType",
            "credentialNumber",

            # Insurance
            "insuranceProvider",
            "policyNumber",
            "insuranceExpiration",
            "coverageLimit",

            # Education
            "degree",
            "institution",
            "fieldOfStudy",
            "graduationYear",

            # Application
            "submitted",
            "appliedDate",
            "status",
            "rejectionReason",

            # Documents
            "documents",

            # AI verification
            "aiStatus",
            "aiScore",
        ]

    def get_status(self, obj):
        if not obj.status:
            return ""

        return obj.status.capitalize()

    def get_submitted(self, obj):
        if not obj.submitted_at:
            return ""

        return obj.submitted_at.strftime(
            "%Y-%m-%d"
        )

    def get_appliedDate(self, obj):
        if not obj.created_at:
            return ""

        return obj.created_at.strftime(
            "%Y-%m-%d"
        )

    def get_documents(self, obj):
        """
        Return document metadata without accessing .url.

        This prevents local serialization from requiring the
        configured S3 storage backend.
        """

        documents = []

        if obj.license_document:
            documents.append({
                "type": "license",
                "name": "License Document",
                "fileName": obj.license_document.name,
            })

        if obj.credential_document:
            documents.append({
                "type": "credential",
                "name": "Credential Document",
                "fileName": obj.credential_document.name,
            })

        if obj.insurance_document:
            documents.append({
                "type": "insurance",
                "name": "Insurance Document",
                "fileName": obj.insurance_document.name,
            })

        if obj.degree_document:
            documents.append({
                "type": "degree",
                "name": "Degree Document",
                "fileName": obj.degree_document.name,
            })

        return documents


# ============================================================
# APPOINTMENTS
# ============================================================

class AdminAppointmentSerializer(serializers.ModelSerializer):
    client = serializers.CharField(
        source="client.full_name"
    )

    nutritionist = serializers.CharField(
        source="nutritionist.full_name"
    )

    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            "id",
            "client",
            "nutritionist",
            "date",
            "time",
            "status",
        ]

    def get_date(self, obj):
        if not obj.date:
            return ""

        return obj.date.strftime(
            "%Y-%m-%d"
        )

    def get_time(self, obj):
        if not obj.time:
            return ""

        return obj.time.strftime(
            "%I:%M %p"
        ).lstrip("0")

    def get_status(self, obj):
        mapping = {
            "pending": "Pending",
            "confirmed": "Confirmed",
            "cancelled": "Cancelled",
            "completed": "Confirmed",
        }

        return mapping.get(
            obj.status,
            obj.status.capitalize(),
        )


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
    """
    Shapes health.Food to match the frontend's FoodItem type exactly
    (admin/food-database/page.tsx):

        { id, name, category, calories, protein, carbs, fat,
          servingSize, photoUrl }

    Field mapping:
      - id                -> cast to string (frontend types id as string)
      - calories/protein/carbs/fat -> calories_per_100g/protein_g/
        carbs_g/fat_g directly. These stay TRUE per-100g values because
        FoodDiaryViewSet.perform_create scales them by logged grams for
        the food diary — do not repurpose them as "per serving" values.
      - servingSize       -> serving_label (purely descriptive text,
        not tied to any of the numbers above — see Food model docstring)
      - photoUrl           -> image, absolute URL or null
      - image (write-only) -> accepts the uploaded file on create/update;
        maps directly onto the model's own `image` field.
    """

    id = serializers.CharField(read_only=True)

    calories = serializers.DecimalField(
        source="calories_per_100g", max_digits=7, decimal_places=2,
    )
    protein = serializers.DecimalField(
        source="protein_g", max_digits=6, decimal_places=2,
    )
    carbs = serializers.DecimalField(
        source="carbs_g", max_digits=6, decimal_places=2,
    )
    fat = serializers.DecimalField(
        source="fat_g", max_digits=6, decimal_places=2,
    )

    servingSize = serializers.CharField(
        source="serving_label",
        required=False,
        allow_blank=True,
        max_length=100,
    )

    photoUrl = serializers.SerializerMethodField()

    image = serializers.ImageField(
        write_only=True, required=False, allow_null=True,
    )

    class Meta:
        model = Food
        fields = [
            "id",
            "name",
            "category",
            "calories",
            "protein",
            "carbs",
            "fat",
            "servingSize",
            "photoUrl",
            "image",
        ]

    def get_photoUrl(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")

        try:
            url = obj.image.url
        except Exception:
            return None

        return request.build_absolute_uri(url) if request else url


# ============================================================
# ADMIN PROFILE
# ============================================================

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "role",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "role",
            "is_active",
        ]


# ============================================================
# FOOD VENDORS
# ============================================================

class AdminFoodVendorSerializer(serializers.ModelSerializer):

    businessName = serializers.CharField(
        source="business_name",
        read_only=True
    )

    ownerName = serializers.CharField(
        source="user.full_name",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    address = serializers.CharField(
        source="business_address",
        read_only=True
    )

    businessLicenseNumber = serializers.CharField(
        source="license_number",
        read_only=True
    )

    foodSafetyCertNumber = serializers.SerializerMethodField()

    appliedDate = serializers.SerializerMethodField()

    status = serializers.CharField(
        source="get_status_display",
        read_only=True
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

        return obj.food_safety_certificate.name.rsplit(
            "/",
            1
        )[-1]

    def get_appliedDate(self, obj):
        if not obj.created_at:
            return ""

        return obj.created_at.strftime(
            "%Y-%m-%d"
        )

    def _file_url(self, request, field_file):
        """
        Safely generate an absolute file URL.

        If the configured storage backend is unavailable,
        return None instead of crashing the entire API response.
        """

        if not field_file:
            return None

        try:
            url = field_file.url

            if request:
                return request.build_absolute_uri(url)

            return url

        except Exception:
            return None

    def get_documents(self, obj):
        request = self.context.get("request")

        docs = []

        if obj.license_document:
            docs.append({
                "label": "Business License",
                "fileName": obj.license_document.name.rsplit(
                    "/",
                    1
                )[-1],
                "fileUrl": self._file_url(
                    request,
                    obj.license_document,
                ),
            })

        if obj.food_safety_certificate:
            docs.append({
                "label": "Food Safety Certificate",
                "fileName": obj.food_safety_certificate.name.rsplit(
                    "/",
                    1
                )[-1],
                "fileUrl": self._file_url(
                    request,
                    obj.food_safety_certificate,
                ),
            })

        if obj.owner_id_document:
            docs.append({
                "label": "Owner ID",
                "fileName": obj.owner_id_document.name.rsplit(
                    "/",
                    1
                )[-1],
                "fileUrl": self._file_url(
                    request,
                    obj.owner_id_document,
                ),
            })

        return docs