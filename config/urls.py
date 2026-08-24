from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "api/nutritionists/",
        include("nutritionists.urls")
    ),
    path("api/auth/", include("accounts.urls")),
    path("api/health/", include("health.urls")),
    path("api/consultations/", include("consultations.urls")),
    path("api/auth/admin/", include("admin_panel.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)