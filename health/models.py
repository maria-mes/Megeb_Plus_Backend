# models.py
from django.db import models
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
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.email} - {self.weight_kg}kg @ {self.logged_at}"


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="exercise_logs"
    )
    activity_type = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField()
    calories_burned = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} ({self.duration_minutes} min)"