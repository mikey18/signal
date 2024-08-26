from django.urls import path
from Generate_signals.consumers import (
    PremiumCheckConsumer_Free,
    # PremiumCheckConsumer
)

url_pattern = [
    path("ws/check/premium/", PremiumCheckConsumer_Free.as_asgi()),
]
