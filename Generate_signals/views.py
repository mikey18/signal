from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import CursorPagination
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from .models import Trade_History
from .serializers import Trade_HistorySerializer
from utils.CustomQuery import get_if_exists
from signals_auth.models import User, MT5Account
from signals_auth.utils.auth_utils import jwt_required
from datetime import datetime, timedelta
from django.utils import timezone


@method_decorator(gzip_page, name="dispatch")
class Trade_History_Calculation_API(APIView):
    def calculate_profit(self, days):
        # Find the last balance from 'days' ago
        start_date = datetime.now() - timedelta(days=days)
        aware_datetime = timezone.make_aware(start_date)
        start_balance = (
            Trade_History.objects.filter(
                account=self.account, created_at__lte=aware_datetime
            )
            .order_by("created_at")
            .values("balance")
            .first()
        )

        # Get the current balance
        current_balance = (
            Trade_History.objects.filter(account=self.account)
            .order_by("-created_at")
            .values("balance")
            .first()
        )

        if start_balance and current_balance:

            # Calculate profit
            return current_balance["balance"] - start_balance["balance"]
        return 0

    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)

            if not user:
                return Response(
                    {"msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.account = get_if_exists(MT5Account, master=True)
            if not self.account:
                return Response(
                    {"msg": "Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            data = {
                1: self.calculate_profit(0),
                30: self.calculate_profit(30),
                90: self.calculate_profit(90),
            }
            return Response({"data": data})
        except Exception as e:
            print(str(e))


class CustomCursorPagination(CursorPagination):
    ordering = "-created_at"
    page_size = 5


@method_decorator(gzip_page, name="dispatch")
class Trade_HistoryAPI(APIView, CustomCursorPagination):
    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)

            if not user:
                return Response(
                    {"msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            account = get_if_exists(MT5Account, master=True)
            if not account:
                return Response(
                    {"msg": "Trade Account not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            orders = Trade_History.objects.filter(account__master=True).order_by(
                "-created_at"
            )
            results = self.paginate_queryset(orders, request, view=self)[:90]
            serializer = Trade_HistorySerializer(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
