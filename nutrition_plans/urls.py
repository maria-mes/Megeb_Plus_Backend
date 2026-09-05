from django.urls import path

from .views import (
    ClientListView,
    FoodListView,
    MealLibraryView,
    MealLibraryDetailView,
    NutritionPlanDetailView,
    NutritionPlanListCreateView,
    NutritionPlanApproveView,
)

urlpatterns = [

    # Nutrition plans
    path(
        "nutrition-plans/",
        NutritionPlanListCreateView.as_view(),
        name="nutrition-plan-list-create",
    ),
    

    path(
        "nutrition-plans/<int:plan_id>/",
        NutritionPlanDetailView.as_view(),
        name="nutrition-plan-detail",
    ),

    # Clients
    path(
        "clients/",
        ClientListView.as_view(),
        name="nutrition-plan-clients",
    ),

    # Food database
    path(
        "foods/",
        FoodListView.as_view(),
        name="nutrition-plan-foods",
    ),

    # Meal library
    path(
        "meal-library/",
        MealLibraryView.as_view(),
        name="meal-library",
    ),
    path(
        "meal-library/<int:meal_id>/",
        MealLibraryDetailView.as_view(),
        name="meal-library-detail"
    ),
    path(
    "nutrition-plans/<int:plan_id>/approve/",
    NutritionPlanApproveView.as_view(),
    name="nutrition-plan-approve",
),
]