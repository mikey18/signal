from django.urls import path
from .views import Trade_History_Calculation_API, Trade_HistoryAPI

urlpatterns = [
    path(
        "history-logic/",
        Trade_History_Calculation_API.as_view(),
        name="trade-history-logic",
    ),
    path(
        "history/",
        Trade_HistoryAPI.as_view(),
        name="trade-history",
    )
]
