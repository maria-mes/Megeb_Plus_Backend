from rest_framework.routers import DefaultRouter
from .views import (
    HealthProfileViewSet, WeightLogViewSet,
    NutritionGoalViewSet, WaterLogViewSet, ExerciseLogViewSet,
    FoodViewSet, FoodEntryViewSet,
)

router = DefaultRouter()
router.register(r'health-profile', HealthProfileViewSet, basename='health-profile')
router.register(r'weight-logs', WeightLogViewSet, basename='weight-log')
router.register(r'nutrition-goals', NutritionGoalViewSet, basename='nutrition-goal')
router.register(r'water-logs', WaterLogViewSet, basename='water-log')
router.register(r'exercise-logs', ExerciseLogViewSet, basename='exercise-log')
router.register(r'foods', FoodViewSet, basename='food')
router.register(r'food-entries', FoodEntryViewSet, basename='food-entry')

urlpatterns = router.urls