from django.urls import path

from .views import (
    NutritionistAppointmentListView,
    ClientAppointmentListView,
    AppointmentCreateView,
    ConfirmAppointmentView,
    CancelAppointmentView,
    CreateConsultationView,
    StartConsultationView,
    NutritionistAvailabilityView,
    NutritionistAvailabilityDetailView,
)


urlpatterns = [
    path(
        "nutritionist/",
        NutritionistAppointmentListView.as_view(),
        name="nutritionist-appointments",
    ),
    path(
    "availability/",
    NutritionistAvailabilityView.as_view(),
    name="nutritionist-availability",
),

path(
    "availability/<int:availability_id>/",
    NutritionistAvailabilityDetailView.as_view(),
    name="nutritionist-availability-detail",
),
    path(
    "consultations/<int:consultation_id>/start/",
    StartConsultationView.as_view(),
    name="start-consultation",
),
    path(
    "<int:appointment_id>/consultation/",
    CreateConsultationView.as_view(),
    name="create-consultation",
),

    path(
        "client/",
        ClientAppointmentListView.as_view(),
        name="client-appointments",
    ),
    path(
    "",
    AppointmentCreateView.as_view(),
    name="appointment-create",
),
    path(
    "<int:appointment_id>/confirm/",
    ConfirmAppointmentView.as_view(),
    name="appointment-confirm",
),
    path(
    "<int:appointment_id>/cancel/",
    CancelAppointmentView.as_view(),
    name="appointment-cancel",
),
]