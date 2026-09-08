from django.urls import path
from .views import (
    AdminUserListView, AdminUserDetailView,
    AdminNutritionistListView, AdminNutritionistDetailView,
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

# No trailing slashes on any path: the (unedited) frontend's commented
# apiFetch calls consistently omit them, and Django's APPEND_SLASH
# redirect doesn't reliably survive PATCH/PUT/POST bodies. Matching
# exactly here avoids relying on that redirect at all.
urlpatterns = [
    path("users", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:user_id>", AdminUserDetailView.as_view(), name="admin-user-detail"),

    path("nutritionists", AdminNutritionistListView.as_view(), name="admin-nutritionists"),
    path("nutritionists/<int:application_id>", AdminNutritionistDetailView.as_view(), name="admin-nutritionist-detail"),

    path("appointments", AdminAppointmentListView.as_view(), name="admin-appointments"),

    path("reports/overview", AdminReportsView.as_view(), name="admin-reports-overview"),

    path("dashboard/stats", AdminDashboardStatsView.as_view(), name="admin-dashboard-stats"),

    path("settings", AdminSettingsView.as_view(), name="admin-settings"),

    path("food", AdminFoodListView.as_view(), name="admin-food"),

    path("profile", AdminProfileView.as_view(), name="admin-profile"),
    path("profile/password", AdminChangePasswordView.as_view(), name="admin-profile-password"),

    path("verification-requests", AdminVerificationRequestsView.as_view(), name="admin-verification-requests"),
    path("verification-requests/count", AdminVerificationCountView.as_view(), name="admin-verification-count"),
    path("food-vendors", AdminFoodVendorListView.as_view(), name="admin-food-vendors"),
    path("food-vendors/<int:application_id>", AdminFoodVendorDetailView.as_view(), name="admin-food-vendor-detail"),
    path("food-vendors/count", AdminFoodVendorCountView.as_view(), name="admin-food-vendor-count")

]