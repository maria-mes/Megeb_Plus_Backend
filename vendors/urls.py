from django.urls import path

from .views import (
    VendorRegistrationView,
    MyVendorApplicationView,
    VendorProfileView,
    VendorProductListCreateView,
    VendorProductDetailView,
    AdminVendorApplicationListView,
    AdminVendorApplicationReviewView,
)

urlpatterns = [

    # Registration
    path(
        "register/",
        VendorRegistrationView.as_view(),
        name="vendor-register",
    ),

    # Application
    path(
        "application/",
        MyVendorApplicationView.as_view(),
        name="vendor-application",
    ),

    # Profile
    path(
        "profile/",
        VendorProfileView.as_view(),
        name="vendor-profile",
    ),

    # Products
    path(
        "products/",
        VendorProductListCreateView.as_view(),
        name="vendor-products",
    ),

    path(
        "products/<int:product_id>/",
        VendorProductDetailView.as_view(),
        name="vendor-product-detail",
    ),

    # Admin
    path(
        "admin/applications/",
        AdminVendorApplicationListView.as_view(),
        name="admin-vendor-applications",
    ),

    path(
        "admin/applications/<int:application_id>/review/",
        AdminVendorApplicationReviewView.as_view(),
        name="admin-vendor-application-review",
    ),
]
