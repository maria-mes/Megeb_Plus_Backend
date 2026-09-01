# models.py
from django.db import models
from django.utils import timezone
from accounts.models import User


class HealthProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extra_active', 'Extra Active'),
    ]

    FASTING_PREFERENCE_CHOICES = [
        ('none', 'No Fasting'),
        ('16_8', '16:8'),
        ('18_6', '18:6'),
        ('20_4', '20:4'),
        ('omad', 'OMAD (One Meal a Day)'),
        ('alternate_day', 'Alternate Day Fasting'),
        ('other', 'Other'),
    ]

    PRIMARY_GOAL_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Build Muscle'),
        ('improve_health', 'Improve Health'),
        ('manage_condition', 'Manage a Health Condition'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="health_profile"
    )

    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    activity_level = models.CharField(
        max_length=50,
        choices=ACTIVITY_LEVEL_CHOICES,
        null=True,
        blank=True
    )

    medical_conditions = models.JSONField(
        default=list,
        blank=True
    )

    allergies = models.JSONField(
        default=list,
        blank=True
    )

    dietary_preferences = models.JSONField(
        default=list,
        blank=True
    )

    # --- New fields ---
    meals_per_day = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="From lifestyle screen"
    )
    fasting_preference = models.CharField(
        max_length=20,
        choices=FASTING_PREFERENCE_CHOICES,
        null=True,
        blank=True,
        help_text="From nutrition screen"
    )
    primary_goal = models.CharField(
        max_length=30,
        choices=PRIMARY_GOAL_CHOICES,
        null=True,
        blank=True,
        help_text="From health-goals screen"
    )

    # --- Calculated nutrition targets ---
    # Auto-computed server-side (see health/utils.py) whenever the profile
    # has enough data — mirrors calculateAndSaveNutritionGoals() on mobile.
    # Never set these directly from client input.
    calorie_target = models.PositiveIntegerField(null=True, blank=True)
    protein_target_g = models.PositiveIntegerField(null=True, blank=True)
    carbs_target_g = models.PositiveIntegerField(null=True, blank=True)
    fat_target_g = models.PositiveIntegerField(null=True, blank=True)
    water_target_glasses = models.PositiveIntegerField(null=True, blank=True)
    water_glass_size_ml = models.PositiveIntegerField(default=250)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health Profile - {self.user.email}"


class WeightLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="weight_logs"
    )
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)

    # The calendar day this weight applies to. Distinct from logged_at
    # (server timestamp) so a user can log for "today" specifically and
    # re-logging the same day updates the existing entry rather than
    # creating a duplicate — see WeightLogViewSet.create().
    date = models.DateField(default=timezone.localdate)

    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'],
                name='unique_weight_log_per_user_per_date'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.weight_kg}kg @ {self.date}"


class NutritionGoal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('lose_weight', 'Lose Weight'),
        ('gain_weight', 'Gain Weight'),
        ('maintain_weight', 'Maintain Weight'),
        ('build_muscle', 'Build Muscle'),
        ('improve_health', 'Improve Health'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="nutrition_goals"
    )
    goal_type = models.CharField(max_length=30, choices=GOAL_TYPE_CHOICES)
    target_weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.goal_type} ({self.status})"


class WaterLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="water_logs"
    )
    amount_ml = models.PositiveIntegerField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.email} - {self.amount_ml}ml @ {self.logged_at}"


class ExerciseLog(models.Model):
    INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exercise_logs"
    )
    activity_type = models.CharField(max_length=100)
    intensity = models.CharField(
        max_length=10,
        choices=INTENSITY_CHOICES,
        default='moderate'
    )
    duration_minutes = models.PositiveIntegerField()

    # Always server-calculated from duration_minutes + intensity
    # (see CALORIES_PER_MINUTE in views.py) — never trust a client value.
    calories_burned = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # The day this activity is logged against — lets a user log for
    # today or a recent past day, distinct from logged_at (server timestamp).
    date = models.DateField(default=timezone.localdate)

    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-logged_at']

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} ({self.duration_minutes} min) @ {self.date}"


class Food(models.Model):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, null=True, blank=True)

    calories_per_100g = models.DecimalField(max_digits=7, decimal_places=2)
    protein_g = models.DecimalField(max_digits=6, decimal_places=2)
    carbs_g = models.DecimalField(max_digits=6, decimal_places=2)
    fat_g = models.DecimalField(max_digits=6, decimal_places=2)
    fiber_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodEntry(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="food_entries"
    )

    # Nullable: lets an entry survive even if the underlying Food
    # is later edited/removed, and supports future "custom food" entries
    # that aren't tied to a catalog row.
    food = models.ForeignKey(
        Food,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries"
    )

    food_name = models.CharField(max_length=150)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    date = models.DateField()

    portion_label = models.CharField(max_length=100, blank=True)
    grams = models.DecimalField(max_digits=7, decimal_places=2)

    # Snapshot of nutrition at the time of logging (grams * food ratios),
    # so historical entries never change if the Food catalog is edited later.
    calories = models.DecimalField(max_digits=7, decimal_places=2)
    protein_g = models.DecimalField(max_digits=6, decimal_places=2)
    carbs_g = models.DecimalField(max_digits=6, decimal_places=2)
    fat_g = models.DecimalField(max_digits=6, decimal_places=2)
    fiber_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'logged_at']

    def __str__(self):
        return f"{self.user.email} - {self.food_name} ({self.meal_type}) @ {self.date}"


class AISuggestion(models.Model):
    """
    A cached, LLM-generated tip for a user's dashboard.
    One per user per day — see health/ai.py for generation logic
    and AISuggestionView for the cache/refresh behavior.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_suggestions"
    )
    date = models.DateField(default=timezone.localdate)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'],
                name='unique_ai_suggestion_per_user_per_date'
            )
        ]

    def __str__(self):
        return f"{self.user.email} - AI suggestion @ {self.date}"