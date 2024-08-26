from django.urls import path
from .views import (
    Register_Push_Notification,
    # Test_Push_Notification_Sync,
    # Test_Push_Notification_Async
)


urlpatterns = [
    path("register_notification/", Register_Push_Notification.as_view()),
    # path("test_notification_sync/", Test_Push_Notification_Sync.as_view()),
    # path('test_notification_async/', Test_Push_Notification_Async.as_view()),
]
