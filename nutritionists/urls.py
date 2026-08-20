from django.urls import path

from .views import (
    NutritionistApplicationCreateView,
    MyNutritionistApplicationView,
    NutritionistApplicationReviewView,
    NutritionistProfileView,
)


urlpatterns = [

    path(
        "apply/",
        NutritionistApplicationCreateView.as_view(),
        name="nutritionist-apply",
    ),

    path(
        "my-application/",
        MyNutritionistApplicationView.as_view(),
        name="my-nutritionist-application",
    ),

    path(
        "applications/<int:application_id>/review/",
        NutritionistApplicationReviewView.as_view(),
        name="nutritionist-application-review",
    ),

    path(
        "profile/",
        NutritionistProfileView.as_view(),
        name="nutritionist-profile",
    ),
]