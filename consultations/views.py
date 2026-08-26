from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response

from .models import AvailabilitySlot, Appointment
from .serializers import AvailabilitySlotSerializer, AppointmentSerializer
from .permissions import IsNutritionist, IsSlotOwner, IsAppointmentParticipant


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """
    Nutritionists create/manage their own availability slots.
    Everyone else can only list open (unbooked) slots, optionally
    filtered by ?nutritionist=<id>.
    """

    serializer_class = AvailabilitySlotSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsNutritionist(), IsSlotOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.role == "nutritionist":
            # Nutritionists see all of their own slots, booked or not.
            return AvailabilitySlot.objects.filter(nutritionist=user)

        # Everyone else only sees open slots available to book.
        queryset = AvailabilitySlot.objects.filter(is_booked=False)
        nutritionist_id = self.request.query_params.get("nutritionist")
        if nutritionist_id:
            queryset = queryset.filter(nutritionist_id=nutritionist_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(nutritionist=self.request.user)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Users book against an open AvailabilitySlot (creates an Appointment,
    flips the slot to booked). Nutritionists confirm/complete/cancel;
    clients can cancel their own.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppointmentParticipant]

    def get_queryset(self):
        user = self.request.user
        if user.role == "nutritionist":
            return Appointment.objects.filter(slot__nutritionist=user).order_by("-created_at")
        return Appointment.objects.filter(user=user).order_by("-created_at")

    def perform_create(self, serializer):
        slot = serializer.validated_data["slot"]

        if slot.is_booked:
            raise serializers.ValidationError({"slot_id": "This slot is already booked."})

        serializer.save(user=self.request.user, status="pending")
        slot.is_booked = True
        slot.save()

    def partial_update(self, request, *args, **kwargs):
        appointment = self.get_object()
        new_status = request.data.get("status")
        valid_statuses = dict(Appointment.STATUS_CHOICES)

        if new_status not in valid_statuses:
            return Response(
                {"detail": f"status must be one of {list(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_nutritionist = appointment.slot.nutritionist == request.user
        is_client = appointment.user == request.user

        if new_status in ["confirmed", "completed"] and not is_nutritionist:
            return Response(
                {"detail": "Only the nutritionist can confirm or complete this appointment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if new_status == "cancelled" and not (is_nutritionist or is_client):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        appointment.status = new_status
        appointment.save()

        # Cancelling frees the slot back up for someone else to book.
        if new_status == "cancelled":
            appointment.slot.is_booked = False
            appointment.slot.save()

        return Response(AppointmentSerializer(appointment).data)