from rest_framework import viewsets, permissions, filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import (
    HealthProfile, WeightLog, NutritionGoal, WaterLog, ExerciseLog,
    Food, FoodEntry, AISuggestion,
)
from .permissions import IsOwner
from .utils import maybe_recalculate_targets
from .ai import generate_ai_suggestion, FALLBACK_MESSAGE_EMPTY
from .serializers import (
    HealthProfileSerializer,
    WeightLogSerializer,
    NutritionGoalSerializer,
    WaterLogSerializer,
    ExerciseLogSerializer,
    FoodSerializer,
    FoodEntrySerializer,
    AISuggestionSerializer,
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


def refresh_ai_suggestion_for_today(user):
    """
    Regenerates and caches today's AI suggestion for `user` right now,
    instead of waiting for the next GET /ai-suggestion/ call. Used
    whenever something happens that should make the tip stale — e.g.
    a new meal is logged, or the user logs in.

    Deliberately swallows any error: this is a "nice to have, refresh
    it if we can" call. A slow/failed Gemini request should never
    block or break the action that triggered it (logging food,
    logging in, etc.) — generate_ai_suggestion() already falls back
    to a safe static message internally, so this just makes sure that
    fallback (or a real tip) gets cached under today's date either way.
    """
    today = timezone.localdate()
    try:
        message = generate_ai_suggestion(user)
        AISuggestion.objects.update_or_create(
            user=user,
            date=today,
            defaults={'message': message},
        )
    except Exception:
        # Never let a suggestion-refresh failure bubble up into the
        # request that triggered it (food logging, login, etc).
        pass


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
        # Meal just changed today's nutrition totals — regenerate the
        # cached AI tip now so the next GET reflects this entry,
        # instead of serving a stale pre-meal cached message.
        refresh_ai_suggestion_for_today(self.request.user)


class AISuggestionView(APIView):
    """
    Returns today's AI-generated nutrition tip for the logged-in user.
    Cached per user per day — only calls the LLM once daily unless
    ?refresh=true is passed. Falls back to a safe static message if
    the LLM call fails or isn't configured (see health/ai.py).

    FIX: previously, the very first call of the day (before any food
    was logged) would cache the "log your first meal" fallback message
    and then return that same stale row for the rest of the day, even
    after the user started logging meals. Now that specific fallback
    message is never treated as a valid cache hit — it keeps
    recomputing live until the user has real data, then locks in
    normally for the day.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        force_refresh = request.query_params.get('refresh') == 'true'

        if not force_refresh:
            existing = AISuggestion.objects.filter(user=request.user, date=today).first()
            # Only treat this as a real cache hit if it isn't the
            # "nothing logged yet" placeholder — that one should never
            # stick around once the user actually starts logging food.
            if existing and existing.message != FALLBACK_MESSAGE_EMPTY:
                return Response(AISuggestionSerializer(existing).data)

        message = generate_ai_suggestion(request.user)

        suggestion, _ = AISuggestion.objects.update_or_create(
            user=request.user,
            date=today,
            defaults={'message': message},
        )

        return Response(AISuggestionSerializer(suggestion).data)


# NOTE ON LOGIN TRIGGER:
# To also regenerate the AI tip whenever a user logs in, call
# refresh_ai_suggestion_for_today(user) from your login view/serializer
# in the accounts app, right after authentication succeeds — e.g.:
#
#     from health.views import refresh_ai_suggestion_for_today
#     refresh_ai_suggestion_for_today(user)
#
# This file doesn't contain the login view, so that call needs to be
# added over there. Paste accounts/views.py (or wherever
# /api/auth/login/ is implemented) and this comment block will be
# replaced with the actual wired-in call.