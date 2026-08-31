from rest_framework import viewsets, permissions, filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils import timezone

from .models import (
    HealthProfile, WeightLog, NutritionGoal, WaterLog, ExerciseLog,
    Food, FoodEntry,
)
from .permissions import IsOwner
from .utils import maybe_recalculate_targets
from .serializers import (
    HealthProfileSerializer,
    WeightLogSerializer,
    NutritionGoalSerializer,
    WaterLogSerializer,
    ExerciseLogSerializer,
    FoodSerializer,
    FoodEntrySerializer,
)


class HealthProfileViewSet(viewsets.ModelViewSet):
    serializer_class = HealthProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # OneToOne with user -> at most one record per user
        return HealthProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if HealthProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError(
                "You already have a health profile. Use PATCH/PUT to update it instead."
            )
        profile = serializer.save(user=self.request.user)
        maybe_recalculate_targets(profile)

    def perform_update(self, serializer):
        profile = serializer.save()
        maybe_recalculate_targets(profile)


class WeightLogViewSet(viewsets.ModelViewSet):
    serializer_class = WeightLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return WeightLog.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Enforce one WeightLog per user per date: if today (or the given
        # date) already has an entry, update it instead of creating a
        # duplicate — mirrors upsertWeight() on the mobile app.
        date = request.data.get('date') or timezone.localdate().isoformat()
        existing = WeightLog.objects.filter(user=request.user, date=date).first()

        if existing:
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, date=date)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NutritionGoalViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionGoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return NutritionGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WaterLogViewSet(viewsets.ModelViewSet):
    serializer_class = WaterLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return WaterLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Calories-per-minute by intensity — mirrors services/activity.ts
# calculateCaloriesBurned() on the mobile app, so the two stay in sync.
CALORIES_PER_MINUTE = {
    'low': 4,
    'moderate': 7,
    'high': 10,
}


class ExerciseLogViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = ExerciseLog.objects.filter(user=self.request.user)
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        return qs

    def _calculate_calories(self, duration_minutes, intensity):
        per_minute = CALORIES_PER_MINUTE.get(intensity, CALORIES_PER_MINUTE['moderate'])
        return round(duration_minutes * per_minute)

    def perform_create(self, serializer):
        duration = serializer.validated_data.get('duration_minutes', 0)
        intensity = serializer.validated_data.get('intensity', 'moderate')
        calories = self._calculate_calories(duration, intensity)
        serializer.save(user=self.request.user, calories_burned=calories)

    def perform_update(self, serializer):
        duration = serializer.validated_data.get(
            'duration_minutes', serializer.instance.duration_minutes
        )
        intensity = serializer.validated_data.get(
            'intensity', serializer.instance.intensity
        )
        calories = self._calculate_calories(duration, intensity)
        serializer.save(calories_burned=calories)


class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only catalog of foods. Supports ?search=<query>, matching
    against name and category — mirrors the mobile app's searchFoods().
    """
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']


class FoodEntryViewSet(viewsets.ModelViewSet):
    """
    A user's logged food diary entries.
    Supports ?date=YYYY-MM-DD to fetch a single day's entries
    (all meal types) — matches getFoodDiaryForDate() on mobile.
    """
    serializer_class = FoodEntrySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = FoodEntry.objects.filter(user=self.request.user)
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)