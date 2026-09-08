from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    time = serializers.SerializerMethodField()

    dateGroup = serializers.SerializerMethodField()

    class Meta:
        model = Notification

        fields = [
            "id",
            "type",
            "title",
            "message",
            "time",
            "dateGroup",
            "read",
        ]

        read_only_fields = fields

    def get_time(self, obj):
        return obj.created_at.strftime("%I:%M %p")

    def get_dateGroup(self, obj):
        from django.utils import timezone

        local_date = timezone.localtime(obj.created_at).date()
        today = timezone.localdate()

        if local_date == today:
            return "Today"

        if local_date == today - timezone.timedelta(days=1):
            return "Yesterday"

        return local_date.strftime("%B %d, %Y")