from django.db import models
from signals_auth.models import User

devices = {
    ("android", "android"),
    ("ios", "ios"),
    ("web", "web")
}

class Notification_Devices(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    device_id = models.CharField(max_length=200, blank=True, unique=True)
    registration_id = models.TextField(max_length=1000)
    type = models.CharField(max_length=10, choices=devices)

    def __str__(self):
        return self.user.email