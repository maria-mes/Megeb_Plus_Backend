from django.urls import path

from .views import (
    AdminUserListView,
    AdminUserDetailView,

    AdminClientListView,
    AdminClientDetailView,

    AdminNutritionistListView,
    AdminNutritionistDetailView,

    AdminAppointmentListView,

    AdminReportsView,
    AdminDashboardStatsView,
    AdminSettingsView,

    AdminVerificationRequestsView,
    AdminVerificationCountView,

    AdminFoodVendorListView,
    AdminFoodVendorDetailView,
    AdminFoodVendorCountView,

    AdminFoodListView,

    AdminProfileView,
    AdminChangePasswordView,
)


urlpatterns = [
    # Users
    path(
        "users",
        AdminUserListView.as_view(),
        name="admin-users",
    ),

    path(
        "users/<int:user_id>",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),

    # Clients
    path(
        "clients",
        AdminClientListView.as_view(),
        name="admin-clients",
    ),

    path(
        "clients/<int:client_id>",
        AdminClientDetailView.as_view(),
        name="admin-client-detail",
    ),

    # Nutritionists
    path(
        "nutritionists",
        AdminNutritionistListView.as_view(),
        name="admin-nutritionists",
    ),

    path(
        "nutritionists/<int:application_id>",
        AdminNutritionistDetailView.as_view(),
        name="admin-nutritionist-detail",
    ),

    # Appointments
    path(
        "appointments",
        AdminAppointmentListView.as_view(),
        name="admin-appointments",
    ),

    # Reports
    path(
        "reports/overview",
        AdminReportsView.as_view(),
        name="admin-reports-overview",
    ),

    # Dashboard
    path(
        "dashboard/stats",
        AdminDashboardStatsView.as_view(),
        name="admin-dashboard-stats",
    ),

    # Settings
    path(
        "settings",
        AdminSettingsView.as_view(),
        name="admin-settings",
    ),

    # Food
    path(
        "food",
        AdminFoodListView.as_view(),
        name="admin-food",
    ),

    # Profile
    path(
        "profile",
        AdminProfileView.as_view(),
        name="admin-profile",
    ),

    path(
        "profile/password",
        AdminChangePasswordView.as_view(),
        name="admin-profile-password",
    ),

    # Verification
    path(
        "verification-requests",
        AdminVerificationRequestsView.as_view(),
        name="admin-verification-requests",
    ),

    path(
        "verification-requests/count",
        AdminVerificationCountView.as_view(),
        name="admin-verification-count",
    ),

    # Food Vendors
    path(
        "food-vendors",
        AdminFoodVendorListView.as_view(),
        name="admin-food-vendors",
    ),

    path(
        "food-vendors/<int:application_id>",
        AdminFoodVendorDetailView.as_view(),
        name="admin-food-vendor-detail",
    ),

    path(
        "food-vendors/count",
        AdminFoodVendorCountView.as_view(),
        name="admin-food-vendor-count",
    ),
]