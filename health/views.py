from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError

from .models import HealthProfile, WeightLog, NutritionGoal, WaterLog, ExerciseLog
from .permissions import IsOwner
from .serializers import (
    HealthProfileSerializer,
    WeightLogSerializer,
    NutritionGoalSerializer,
    WaterLogSerializer,
    ExerciseLogSerializer,
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
        serializer.save(user=self.request.user)


class WeightLogViewSet(viewsets.ModelViewSet):
    serializer_class = WeightLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return WeightLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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


class ExerciseLogViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ExerciseLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)