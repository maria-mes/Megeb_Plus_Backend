from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Appointment, Consultation, NutritionistAvailability
from .serializers import AppointmentSerializer, ConsultationSerializer, NutritionistAvailabilitySerializer
import uuid
from chat.models import Conversation

class NutritionistAppointmentListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        appointments = Appointment.objects.filter(
            nutritionist=request.user
        ).order_by("date", "time")

        serializer = AppointmentSerializer(
            appointments,
            many=True
        )

        return Response(serializer.data)


class ClientAppointmentListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        appointments = Appointment.objects.filter(
            client=request.user
        ).order_by("date", "time")

        serializer = AppointmentSerializer(
            appointments,
            many=True
        )

        return Response(serializer.data)
class AppointmentCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AppointmentSerializer(
            data=request.data
        )

        if serializer.is_valid():

            appointment = serializer.save()
            Conversation.objects.get_or_create(
            client=appointment.client,
            nutritionist=appointment.nutritionist,
            
)
            return Response(
                AppointmentSerializer(appointment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
class ConfirmAppointmentView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, appointment_id):

        try:
            appointment = Appointment.objects.get(
                id=appointment_id
            )

        except Appointment.DoesNotExist:

            return Response(
                {
                    "detail": "Appointment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Only the assigned nutritionist can confirm
        if appointment.nutritionist != request.user:

            return Response(
                {
                    "detail": "Only the assigned nutritionist can confirm this appointment."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Appointment must still be pending
        if appointment.status != "pending":

            return Response(
                {
                    "detail": "Only pending appointments can be confirmed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = "confirmed"
        appointment.save()

        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
class CancelAppointmentView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, appointment_id):

        try:
            appointment = Appointment.objects.get(
                id=appointment_id
            )

        except Appointment.DoesNotExist:

            return Response(
                {
                    "detail": "Appointment not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Only the client or assigned nutritionist can cancel
        if (
            appointment.client != request.user
            and appointment.nutritionist != request.user
        ):

            return Response(
                {
                    "detail": "You are not allowed to cancel this appointment."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Cannot cancel an already completed appointment
        if appointment.status == "completed":

            return Response(
                {
                    "detail": "Completed appointments cannot be cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cannot cancel an already cancelled appointment
        if appointment.status == "cancelled":

            return Response(
                {
                    "detail": "Appointment is already cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.status = "cancelled"
        appointment.save()

        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )
class CreateConsultationView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):

        try:
            appointment = Appointment.objects.get(
                id=appointment_id
            )

        except Appointment.DoesNotExist:
            return Response(
                {"detail": "Appointment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only the client or nutritionist can create the consultation
        if (
            request.user != appointment.client
            and request.user != appointment.nutritionist
        ):
            return Response(
                {
                    "detail": "You are not part of this appointment."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Appointment must be confirmed
        if appointment.status != "confirmed":
            return Response(
                {
                    "detail": (
                        "A consultation can only be created "
                        "for a confirmed appointment."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Don't create duplicate consultations
        if Consultation.objects.filter(
            appointment=appointment
        ).exists():
            return Response(
                {
                    "detail": "A consultation already exists."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate unique Jitsi room
        room_id = f"megebplus-{uuid.uuid4().hex}"

        meeting_url = (
            f"https://meet.jit.si/{room_id}"
        )

        consultation = Consultation.objects.create(
            appointment=appointment,
            room_id=room_id,
            meeting_id=room_id,
            meeting_url=meeting_url,
        )

        return Response(
            ConsultationSerializer(
                consultation
            ).data,
            status=status.HTTP_201_CREATED
        )
class StartConsultationView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, consultation_id):

        try:
            consultation = Consultation.objects.select_related(
                "appointment"
            ).get(id=consultation_id)

        except Consultation.DoesNotExist:
            return Response(
                {"detail": "Consultation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        appointment = consultation.appointment

        # Only the client or nutritionist can start
        if (
            request.user != appointment.client
            and request.user != appointment.nutritionist
        ):
            return Response(
                {
                    "detail": "You are not part of this consultation."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if consultation.status != "waiting":
            return Response(
                {
                    "detail": "Consultation cannot be started."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate a unique room
        room_id = (
            f"megeb-consultation-{consultation.id}-"
            f"{uuid.uuid4().hex[:10]}"
        )

        meeting_url = f"https://meet.jit.si/{room_id}"

        consultation.status = "active"
        consultation.room_id = room_id
        consultation.meeting_url = meeting_url
        consultation.started_at = timezone.now()

        consultation.save(
            update_fields=[
                "status",
                "room_id",
                "meeting_url",
                "started_at",
                "updated_at",
            ]
        )

        return Response(
            ConsultationSerializer(consultation).data,
            status=status.HTTP_200_OK
        )
class EndConsultationView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, consultation_id):

        try:
            consultation = Consultation.objects.select_related(
                "appointment"
            ).get(id=consultation_id)

        except Consultation.DoesNotExist:
            return Response(
                {"detail": "Consultation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        appointment = consultation.appointment

        if (
            request.user != appointment.client
            and request.user != appointment.nutritionist
        ):
            return Response(
                {
                    "detail": "You are not part of this consultation."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if consultation.status != "active":
            return Response(
                {
                    "detail": "Only active consultations can be ended."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        consultation.status = "completed"
        consultation.ended_at = timezone.now()

        consultation.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        appointment.status = "completed"
        appointment.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return Response(
            ConsultationSerializer(consultation).data,
            status=status.HTTP_200_OK
        )
class NutritionistAvailabilityView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        availability = NutritionistAvailability.objects.filter(
            nutritionist=request.user,
            is_active=True,
        )

        serializer = NutritionistAvailabilitySerializer(
            availability,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = NutritionistAvailabilitySerializer(
            data=request.data
        )

        if serializer.is_valid():

            availability = serializer.save(
                nutritionist=request.user
            )

            return Response(
                NutritionistAvailabilitySerializer(
                    availability
                ).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class NutritionistAvailabilityDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, availability_id):

        try:
            availability = NutritionistAvailability.objects.get(
                id=availability_id,
                nutritionist=request.user,
            )

        except NutritionistAvailability.DoesNotExist:

            return Response(
                {
                    "detail": "Availability slot not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NutritionistAvailabilitySerializer(
            availability,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, availability_id):

        try:
            availability = NutritionistAvailability.objects.get(
                id=availability_id,
                nutritionist=request.user,
            )

        except NutritionistAvailability.DoesNotExist:

            return Response(
                {
                    "detail": "Availability slot not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        availability.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )