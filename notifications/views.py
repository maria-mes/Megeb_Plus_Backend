from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            recipient=request.user
        )

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(serializer.data)


class NotificationReadView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):

        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user,
        )

        notification.read = True

        notification.save(
            update_fields=["read"]
        )

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )


class MarkAllNotificationsReadView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        Notification.objects.filter(
            recipient=request.user,
            read=False,
        ).update(read=True)

        return Response(
            {
                "message": "All notifications marked as read."
            },
            status=status.HTTP_200_OK,
        )