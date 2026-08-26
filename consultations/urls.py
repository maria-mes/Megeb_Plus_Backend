from rest_framework.routers import DefaultRouter
from .views import AvailabilitySlotViewSet, AppointmentViewSet

router = DefaultRouter()
router.register(r'slots', AvailabilitySlotViewSet, basename='availability-slot')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = router.urls