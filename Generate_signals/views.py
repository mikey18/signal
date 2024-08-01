from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework import status
from .models import Trade_History
from .serializers import Trade_HistorySerializer
from signals_auth.functions.auth_functions import auth_decoder
from functions.CustomQuery import get_if_exists
from signals_auth.models import User, MT5Account


@method_decorator(gzip_page, name="dispatch")
class Trade_HistoryAPI(APIView):
    def get(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            user = get_if_exists(User, id=payload["id"])

            if not user:
                return Response(
                    {"status": 400, "msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            account = get_if_exists(MT5Account, user__id=payload["id"])
            if not account:
                return Response(
                    {"status": 400, "msg": "Trade Account not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            orders = Trade_History.objects.filter(account__master=True).order_by(
                "-created_at"
            )
            # orders = Trade_History.objects.filter(account=account).order_by('-created_at')
            serializer = Trade_HistorySerializer(orders, many=True)
            return Response({"status": 200, "data": serializer.data})
        except Exception:
            return Response(
                {"status": 400, "msg": "Not Authorized"},
                status=status.HTTP_400_BAD_REQUEST,
            )
