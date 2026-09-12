# health/utils.py
"""
Server-side mirror of utils/nutritionCalculator.ts on the mobile app.
Keep this in sync if that formula ever changes there.
"""
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

# HealthProfile.activity_level (mobile's 4-value vocabulary, see
# models.py ACTIVITY_LEVEL_CHOICES) -> the calculator's activity
# vocabulary (5 buckets — 'moderate' is simply never reached, since
# mobile only ever sends one of these 4 values).
ACTIVITY_LEVEL_MAP = {
    'mostly-sitting': 'sedentary',
    'light': 'light',
    'active': 'active',
    'very-active': 'very_active',
}

# HealthProfile.health_goal (mobile's 8-value vocabulary, see models.py
# HEALTH_GOAL_CHOICES — was primary_goal before this fix) -> the
# calculator's goal vocabulary. Only weight-loss/muscle-gain map to a
# non-default bucket; the rest (energy, healthy-eating, digestion,
# fasting-routine, support-health, other) have no calorie-adjustment
# equivalent on mobile, so they're treated as maintenance.
GOAL_MAP = {
    'weight-loss': 'lose_weight',
    'muscle-gain': 'gain_weight',
    'energy': 'maintain_weight',
    'healthy-eating': 'maintain_weight',
    'digestion': 'maintain_weight',
    'fasting-routine': 'maintain_weight',
    'support-health': 'maintain_weight',
    'other': 'maintain_weight',
}

ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}


def calculate_nutrition_goals(*, sex, age, height_cm, weight_kg, activity_level, goal):
    """
    Mirrors calculateNutritionGoals() in utils/nutritionCalculator.ts exactly.

    sex: 'male' | 'female'
    activity_level / goal: already mapped via ACTIVITY_LEVEL_MAP / GOAL_MAP
    """
    weight_kg = float(weight_kg)
    height_cm = float(height_cm)
    age = float(age)

    if sex == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    calories = bmr * ACTIVITY_MULTIPLIERS[activity_level]

    if goal == 'lose_weight':
        calories -= 300
    if goal == 'gain_weight':
        calories += 300

    calories = round(max(calories, 1200))

    protein_target_g = round(weight_kg * 1.6)
    fat_target_g = round((calories * 0.25) / 9)

    protein_calories = protein_target_g * 4
    fat_calories = fat_target_g * 9

    carbs_target_g = round(max(calories - protein_calories - fat_calories, 0) / 4)

    water_target_glasses = max(6, round(weight_kg * 0.033 / 0.25))

    return {
        'calorie_target': calories,
        'protein_target_g': protein_target_g,
        'carbs_target_g': carbs_target_g,
        'fat_target_g': fat_target_g,
        'water_target_glasses': water_target_glasses,
        'water_glass_size_ml': 250,
    }


def maybe_recalculate_targets(profile):
    """
    Recomputes and saves calorie/macro targets on a HealthProfile if enough
    data is present — mirrors the isProfileComplete check inside
    calculateAndSaveNutritionGoals() on mobile. Leaves existing targets
    untouched if the profile is incomplete or gender is 'other' (the
    Mifflin-St Jeor formula only has male/female branches).
    """
    has_required_fields = (
        profile.age is not None
        and profile.height_cm is not None
        and profile.weight_kg is not None
        and profile.gender in ('male', 'female')
        and bool(profile.activity_level)
        and bool(profile.health_goal)
    )

    if not has_required_fields:
        return profile

    mapped_activity = ACTIVITY_LEVEL_MAP.get(profile.activity_level)
    mapped_goal = GOAL_MAP.get(profile.health_goal, 'maintain_weight')

    if not mapped_activity:
        return profile

    targets = calculate_nutrition_goals(
        sex=profile.gender,
        age=profile.age,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=mapped_activity,
        goal=mapped_goal,
    )

    for field, value in targets.items():
        setattr(profile, field, value)

    profile.save(update_fields=list(targets.keys()) + ['updated_at'])

    return profile


# --- Streaks ---
# A day "counts" toward the streak if the user's calorie goal was met
# that day (some food logged, and total calories within tolerance of
# calorie_target). Change the definition in _day_goals_met() only —
# check_and_update_streak() just recomputes the streak by walking
# backward from today using whatever that function returns, so it
# doesn't need to change if the definition does (e.g. adding an
# activity or water requirement later).
#
# check_and_update_streak() is safe to call on ANY request that touches
# a user's health data — including plain GET /dashboard/ reads — because
# it always recomputes from scratch rather than trusting a previously
# stored value. That's what makes "no qualifying activity today -> 0"
# and "if yesterday is missing -> reset" work correctly even if the
# user never logs anything (they just open the dashboard).

CALORIE_GOAL_TOLERANCE = 0.10  # up to 10% over calorie_target still counts as "met"
MAX_STREAK_LOOKBACK_DAYS = 3650  # safety cap so the backward walk can't run forever


def _day_goals_met(user, date):
    """
    True if the calorie goal was met for `date`: some food was logged,
    and total calories are within tolerance of the profile's calorie_target.
    """
    from .models import HealthProfile, FoodEntry  # avoid circular import

    profile = HealthProfile.objects.filter(user=user).first()
    if not profile or not profile.calorie_target:
        return False

    calories_consumed = sum(
        (e.calories for e in FoodEntry.objects.filter(user=user, date=date)),
        Decimal("0"),
    )
    return 0 < calories_consumed <= profile.calorie_target * Decimal(str(1 + CALORIE_GOAL_TOLERANCE))


def check_and_update_streak(user):
    """
    Recomputes the streak from scratch by walking backward from today,
    and persists the result. Safe to call anytime — after a log change,
    or on a plain dashboard read — since it always derives the answer
    fresh rather than trusting the previously stored value.

    Rules:
      - today's calorie goal not met -> streak = 0
      - today's calorie goal met -> count consecutive met days walking
        backward from today; stop at the first day that wasn't met
        (so a missing/failed yesterday resets the count to just today = 1)
    """
    from .models import HealthProfile  # avoid circular import

    profile = HealthProfile.objects.filter(user=user).first()
    if not profile:
        return

    today = timezone.localdate()

    streak = 0
    if _day_goals_met(user, today):
        date = today
        for _ in range(MAX_STREAK_LOOKBACK_DAYS):
            if not _day_goals_met(user, date):
                break
            streak += 1
            date -= timedelta(days=1)

    profile.current_streak_days = streak
    profile.longest_streak_days = max(profile.longest_streak_days, streak)
    profile.last_streak_date = today if streak else None
    profile.save(update_fields=['current_streak_days', 'longest_streak_days', 'last_streak_date'])