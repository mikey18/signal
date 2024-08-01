from django.urls import path
from Generate_signals.consumers import PremiumCheckConsumerNew

url_pattern = [
    path("ws/check/premium/", PremiumCheckConsumerNew.as_asgi()),
]
