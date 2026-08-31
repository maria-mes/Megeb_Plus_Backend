# health/utils.py
"""
Server-side mirror of utils/nutritionCalculator.ts on the mobile app.
Keep this in sync if that formula ever changes there.
"""

# HealthProfile.activity_level -> the calculator's activity vocabulary
ACTIVITY_LEVEL_MAP = {
    'sedentary': 'sedentary',
    'lightly_active': 'light',
    'moderately_active': 'moderate',
    'very_active': 'active',
    'extra_active': 'very_active',
}

# HealthProfile.primary_goal -> the calculator's goal vocabulary
# (build_muscle/improve_health/manage_condition have no direct equivalent
# on mobile, so they're mapped to the closest sensible bucket)
GOAL_MAP = {
    'lose_weight': 'lose_weight',
    'gain_weight': 'gain_weight',
    'maintain_weight': 'maintain_weight',
    'build_muscle': 'gain_weight',
    'improve_health': 'maintain_weight',
    'manage_condition': 'maintain_weight',
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
        and bool(profile.primary_goal)
    )

    if not has_required_fields:
        return profile

    mapped_activity = ACTIVITY_LEVEL_MAP.get(profile.activity_level)
    mapped_goal = GOAL_MAP.get(profile.primary_goal, 'maintain_weight')

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