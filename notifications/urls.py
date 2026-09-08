from django.urls import path , include

from .views import (
    NotificationListView,
    NotificationReadView,
    MarkAllNotificationsReadView,
)


urlpatterns = [
    path(
        "",
        NotificationListView.as_view(),
        name="notifications",
    ),

    path(
        "<int:notification_id>/read/",
        NotificationReadView.as_view(),
        name="notification-read",
    ),

    path(
        "mark-all-read/",
        MarkAllNotificationsReadView.as_view(),
        name="mark-all-read",
    ),
]