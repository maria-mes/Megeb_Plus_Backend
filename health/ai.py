# health/ai.py
"""
Generates a short, personalized nutrition/activity tip using Google
Gemini, based on the user's real logged data for today.

Falls back to a safe static message if anything goes wrong (missing
API key, network issue, rate limit, bad response) so the dashboard
never breaks because of this feature.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from .models import FoodEntry, WaterLog, ExerciseLog, HealthProfile

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE_LOGGED = "Great job logging your meals today! Keep it up."
FALLBACK_MESSAGE_EMPTY = (
    "Log your first meal to get personalised nutrition insights powered by AI."
)


def _gather_today_summary(user):
    today = timezone.localdate()

    food_entries = FoodEntry.objects.filter(user=user, date=today)
    calories_consumed = sum((e.calories for e in food_entries), Decimal("0"))
    protein_consumed = sum((e.protein_g for e in food_entries), Decimal("0"))

    water_ml = sum(
        (log.amount_ml for log in WaterLog.objects.filter(user=user, logged_at__date=today)),
        0,
    )

    activity_minutes = sum(
        (log.duration_minutes for log in ExerciseLog.objects.filter(user=user, date=today)),
        0,
    )

    profile = HealthProfile.objects.filter(user=user).first()

    return {
        "calories_consumed": float(calories_consumed),
        "calorie_target": profile.calorie_target if profile else None,
        "protein_consumed": float(protein_consumed),
        "protein_target": profile.protein_target_g if profile else None,
        "water_ml": water_ml,
        "water_target_glasses": profile.water_target_glasses if profile else None,
        "activity_minutes": activity_minutes,
        "primary_goal": profile.primary_goal if profile else None,
        "has_logged_anything": food_entries.exists(),
    }


def _build_prompt(summary):
    calorie_line = f"Calories today: {summary['calories_consumed']:.0f}"
    if summary["calorie_target"]:
        calorie_line += f" (target {summary['calorie_target']})"

    protein_line = f"Protein today: {summary['protein_consumed']:.0f}g"
    if summary["protein_target"]:
        protein_line += f" (target {summary['protein_target']}g)"

    water_line = f"Water today: {summary['water_ml']}ml"
    if summary["water_target_glasses"]:
        water_line += f" (target ~{summary['water_target_glasses']} glasses)"

    goal_line = f"User's goal: {summary['primary_goal'] or 'general health'}"

    return (
        "You are a friendly nutrition coach inside a health app. "
        "Based on this user's data for today, write ONE short, warm, "
        "actionable tip. Max 25 words. No medical claims, no diagnosis, "
        "no disclaimers — just the tip itself.\n\n"
        f"{calorie_line}\n{protein_line}\n{water_line}\n"
        f"Activity today: {summary['activity_minutes']} minutes\n"
        f"{goal_line}"
    )


def generate_ai_suggestion(user):
    summary = _gather_today_summary(user)

    if not summary["has_logged_anything"]:
        # Nothing logged yet today — no point calling the LLM on empty data.
        return FALLBACK_MESSAGE_EMPTY

    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if not api_key:
        logger.warning("generate_ai_suggestion: GEMINI_API_KEY is not set — using fallback.")
        return FALLBACK_MESSAGE_LOGGED

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.6-flash")

        response = model.generate_content(_build_prompt(summary))
        text = (response.text or "").strip()

        if not text:
            logger.warning(
                "generate_ai_suggestion: Gemini returned an empty response for user_id=%s. "
                "Full response: %r",
                user.id,
                response,
            )

        return text or FALLBACK_MESSAGE_LOGGED

    except Exception:
        # Any failure (missing package, bad key, network, rate limit) —
        # never let this break the dashboard. But DO log it, so we can
        # actually see what's going wrong instead of guessing.
        logger.exception(
            "generate_ai_suggestion: Gemini call failed for user_id=%s — falling back.",
            user.id,
        )
        return FALLBACK_MESSAGE_LOGGED