from django.urls import path
from .views import (Trade_HistoryAPI)

# app_name = 'api'
urlpatterns = [
    path('history/', Trade_HistoryAPI.as_view(), name='trade-signals-history')
]
