from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from notification.models import Notification_Devices
from utils.CustomQuery import get_if_exists
from signals_auth.utils.auth_utils import jwt_required
from django.utils.decorators import method_decorator
from signals_auth.models import User
from utils.notifications import BATCH_PUSH_NOTIFICATION
from django.utils.decorators import method_decorator


@method_decorator(gzip_page, name="dispatch")
class Register_Push_Notification(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)

            if not user:
                return Response(
                    {"status": 400, "msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fcm = get_if_exists(
                Notification_Devices, registration_id=request.data["token"]
            )
            if fcm:
                return Response(
                    {"status": 400, "msg": "Token already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            device = get_if_exists(
                Notification_Devices, device_id=request.data["device_id"]
            )
            if device:
                return Response(
                    {"status": 400, "msg": "Device already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Notification_Devices.objects.create(
                user=user,
                registration_id=request.data["token"],
                type=request.data["type"],
                device_id=request.data["device_id"],
            )
            return Response({"status": 200})
        except Exception as e:
            print(str(e))
            return Response(
                {"status": 500, "msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class Test_Push_Notification_Sync(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)

            if not user:
                return Response(
                    {"status": 400, "msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            BATCH_PUSH_NOTIFICATION(
                user_id=request.user_id,
                title=request.data["title"],
                body=request.data["body"],
            )
            return Response({"status": 200})
        except Exception as e:
            print(str(e))
