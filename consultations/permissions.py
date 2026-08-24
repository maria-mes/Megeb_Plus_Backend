from rest_framework import permissions


class IsNutritionist(permissions.BasePermission):
    """Only allow users with role='nutritionist' to publish availability slots."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "nutritionist"
        )


class IsSlotOwner(permissions.BasePermission):
    """Only allow a nutritionist to edit/delete their own slots."""

    def has_object_permission(self, request, view, obj):
        return obj.nutritionist == request.user


class IsAppointmentParticipant(permissions.BasePermission):
    """Only the client who booked, or the nutritionist being booked, can view/act on an appointment."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or obj.slot.nutritionist == request.user