from rest_framework import serializers
from .models import (
    HealthProfile, WeightLog, NutritionGoal, WaterLog, ExerciseLog,
    Food, FoodEntry, AISuggestion,
)


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = [
            'id', 'user', 'age', 'gender', 'height_cm', 'weight_kg',
            'activity_level', 'medical_conditions', 'allergies',
            'dietary_preferences',
            'meals_per_day', 'fasting_preference', 'primary_goal',
            'calorie_target', 'protein_target_g', 'carbs_target_g',
            'fat_target_g', 'water_target_glasses', 'water_glass_size_ml',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'created_at', 'updated_at',
            'calorie_target', 'protein_target_g', 'carbs_target_g',
            'fat_target_g', 'water_target_glasses', 'water_glass_size_ml',
        ]


class WeightLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightLog
        fields = ['id', 'user', 'weight_kg', 'date', 'logged_at']
        read_only_fields = ['id', 'user', 'logged_at']


class NutritionGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionGoal
        fields = [
            'id', 'user', 'goal_type', 'target_weight_kg',
            'target_date', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


class WaterLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterLog
        fields = ['id', 'user', 'amount_ml', 'logged_at']
        read_only_fields = ['id', 'user', 'logged_at']


class ExerciseLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseLog
        fields = [
            'id', 'user', 'activity_type', 'intensity', 'duration_minutes',
            'calories_burned', 'date', 'logged_at',
        ]
        # calories_burned is computed server-side in the view
        # (from duration_minutes + intensity), never client-supplied.
        read_only_fields = ['id', 'user', 'calories_burned', 'logged_at']


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'category',
            'calories_per_100g', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g',
        ]


class FoodEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodEntry
        fields = [
            'id', 'user', 'food', 'food_name', 'meal_type', 'date',
            'portion_label', 'grams',
            'calories', 'protein_g', 'carbs_g', 'fat_g', 'fiber_g',
            'logged_at',
        ]
        read_only_fields = ['id', 'user', 'logged_at']

    def validate(self, attrs):
        # If a catalog food was picked but food_name wasn't sent explicitly,
        # fill it in from the Food row so the entry is self-contained.
        food = attrs.get('food')
        if food and not attrs.get('food_name'):
            attrs['food_name'] = food.name
        return attrs


class AISuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISuggestion
        fields = ['id', 'message', 'date', 'created_at']
        read_only_fields = fields