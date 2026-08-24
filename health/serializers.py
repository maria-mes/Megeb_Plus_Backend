from rest_framework import serializers
from .models import HealthProfile, WeightLog, NutritionGoal, WaterLog, ExerciseLog


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = [
            'id', 'user', 'age', 'gender', 'height_cm', 'weight_kg',
            'activity_level', 'medical_conditions', 'allergies',
            'dietary_preferences',
            'meals_per_day', 'fasting_preference', 'primary_goal',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WeightLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightLog
        fields = ['id', 'user', 'weight_kg', 'logged_at']
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
            'id', 'user', 'activity_type', 'duration_minutes',
            'calories_burned', 'logged_at',
        ]
        read_only_fields = ['id', 'user', 'logged_at']