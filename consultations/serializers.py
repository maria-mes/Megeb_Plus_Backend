from rest_framework import serializers
from .models import AvailabilitySlot, Appointment


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    nutritionist_name = serializers.CharField(source="nutritionist.full_name", read_only=True)

    class Meta:
        model = AvailabilitySlot
        fields = [
            "id", "nutritionist", "nutritionist_name",
            "date", "start_time", "end_time", "is_booked", "created_at",
        ]
        read_only_fields = ["id", "nutritionist", "is_booked", "created_at"]


class AppointmentSerializer(serializers.ModelSerializer):
    # Write: client sends the slot id they want to book.
    slot_id = serializers.PrimaryKeyRelatedField(
        source="slot",
        queryset=AvailabilitySlot.objects.filter(is_booked=False),
        write_only=True,
    )

    # Read: flattened, human-readable fields pulled from the related slot.
    client_name = serializers.CharField(source="user.full_name", read_only=True)
    nutritionist_name = serializers.CharField(source="slot.nutritionist.full_name", read_only=True)
    date = serializers.DateField(source="slot.date", read_only=True)
    start_time = serializers.TimeField(source="slot.start_time", read_only=True)
    end_time = serializers.TimeField(source="slot.end_time", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id", "user", "client_name", "nutritionist_name",
            "slot_id", "date", "start_time", "end_time",
            "status", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]