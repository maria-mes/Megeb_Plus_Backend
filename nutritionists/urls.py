from django.urls import path

from .views import (
    NutritionistApplicationCreateView,
    MyNutritionistApplicationView,
    NutritionistApplicationReviewView,
    NutritionistProfileView,
    ClientDetailView,
    NutritionistClientsListView
)
from nutrition_plans.views import ClientListView
from .views import NutritionistApplicationAIVerifyView


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
    path(
        "applications/<int:application_id>/ai-verify/",
        NutritionistApplicationAIVerifyView.as_view(),
        name="application-ai-verify",
    ),
   
     path(
        "clients/",
        ClientListView.as_view(),
        name="nutritionist-clients",
    ),

    path(
        "clients/<int:client_id>/",
        ClientDetailView.as_view(),
        name="nutritionist-client-detail",
    ),
]