from django.conf import settings
from django.db import models


class Food(models.Model):
    CATEGORY_CHOICES = [
        ("Protein", "Protein"),
        ("Grains", "Grains"),
        ("Legumes", "Legumes"),
        ("Dairy", "Dairy"),
        ("Fruits", "Fruits"),
        ("Vegetables", "Vegetables"),
        ("Nuts", "Nuts"),
        ("Other", "Other"),
    ]

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Other",
    )

    unit_based = models.BooleanField(default=False)
    unit_name = models.CharField(max_length=50, default="g")
    grams_per_unit = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=100,
    )
    preparation = models.CharField(max_length=100, blank=True, default="")
    serving_description = models.CharField(max_length=255, blank=True, default="")

    calories = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    protein = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    carbs = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    fat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    fiber = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
      ordering = ["name"]
      constraints = [
        models.UniqueConstraint(
            fields=["name", "preparation"],
            name="unique_food_preparation",
        )
    ]

    def __str__(self):
        return self.name


class MealLibrary(models.Model):
    MEAL_TYPE_CHOICES = [
        ("Breakfast", "Breakfast"),
        ("Snack", "Snack"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
    ]

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=255)

    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meal_library",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MealLibraryItem(models.Model):
    id = models.BigAutoField(primary_key=True)

    meal = models.ForeignKey(
        MealLibrary,
        on_delete=models.CASCADE,
        related_name="items",
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.PROTECT,
        related_name="library_items",
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.meal.name} - {self.food.name}"


class NutritionPlan(models.Model):
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Active", "Active"),
        ("Completed", "Completed"),
    ]

    GOAL_CHOICES = [
        ("Weight Management", "Weight Management"),
        ("Healthy Weight Gain", "Healthy Weight Gain"),
        ("Balanced Nutrition", "Balanced Nutrition"),
        ("Diabetes Management", "Diabetes Management"),
        ("Heart Health", "Heart Health"),
        ("Improved Energy", "Improved Energy"),
        ("General Wellness", "General Wellness"),
    ]

    id = models.BigAutoField(primary_key=True)

    nutritionist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_nutrition_plans",
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nutrition_plans",
    )

    plan_name = models.CharField(max_length=255)

    goal = models.CharField(
        max_length=100,
        choices=GOAL_CHOICES,
    )

    start_date = models.DateField()
    end_date = models.DateField()

    target_calories = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Draft",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.plan_name} - {self.client.full_name}"


class PlanMeal(models.Model):
    MEAL_TYPE_CHOICES = [
        ("Breakfast", "Breakfast"),
        ("Snack", "Snack"),
        ("Lunch", "Lunch"),
        ("Dinner", "Dinner"),
    ]

    SOURCE_CHOICES = [
        ("library", "Library"),
        ("custom", "Custom"),
    ]

    id = models.BigAutoField(primary_key=True)

    nutrition_plan = models.ForeignKey(
        NutritionPlan,
        on_delete=models.CASCADE,
        related_name="meals",
    )

    name = models.CharField(max_length=255)

    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="custom",
    )

    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nutrition_plan.plan_name} - {self.name}"


class PlanMealItem(models.Model):
    id = models.BigAutoField(primary_key=True)

    meal = models.ForeignKey(
        PlanMeal,
        on_delete=models.CASCADE,
        related_name="items",
    )

    food = models.ForeignKey(
        Food,
        on_delete=models.PROTECT,
        related_name="plan_items",
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        unique_together = ("meal", "food")

    def __str__(self):
        return f"{self.meal.name} - {self.food.name}"