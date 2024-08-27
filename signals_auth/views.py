from .models import User, MT5Account, Brokers
from Generate_signals.models import Trade_Task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    MT5AccountSerializer,
    UserSerializer,
    BrokersSerializer,
    VerifyAccountSerializer,
)
from .models import OneTimePassword, Devices, OldPassword
from datetime import datetime, timezone
from .utils.auth_utils import access_refresh_token, jwt_required, get_tokens
from utils.CustomQuery import get_if_exists
from Generate_signals.tasks import signal_trade_task
from django.contrib.auth.models import update_last_login
from notification.models import Notification_Devices
import MetaTrader5 as mt5
from dotenv import load_dotenv
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from utils.email import HandleEmail
from django.contrib.auth.hashers import check_password


load_dotenv()


class RefreshTokenView(APIView):
    @method_decorator(jwt_required(token_type="refresh"))
    def post(self, request):
        user = get_if_exists(User, id=request.user_id)
        if not user:
            return Response(
                {
                    "msg": "Invalid auth",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(
            {
                "access": access_refresh_token(user, "access"),
            }
        )


@method_decorator(gzip_page, name="dispatch")
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        HandleEmail.delay(user.id, user.email, user.first_name, "create")
        return Response({"msg": "Successful", "user": serializer.data})


@method_decorator(gzip_page, name="dispatch")
class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def bad_response(self):
        return Response(
            {"msg": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_if_exists(
            User, email=serializer.validated_data["email"].lower(), is_active=True
        )
        if (
            not user
            or not user.check_password(request.data["password"])
            or user.is_superuser
        ):
            return self.bad_response()

        if user.is_verified is False:
            HandleEmail.delay(user.id, user.email, user.first_name, "update")
            return Response(
                {
                    "status": False,
                    "msg": "User not verified",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        devices = get_if_exists(
            Devices, user=user, user_agent=request.META.get("HTTP_USER_AGENT")
        )
        if not devices:
            HandleEmail.delay(user.id, user.email, user.first_name, "update")
            return Response(
                {
                    "status": False,
                    "msg": "Device not registered",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        update_last_login(None, user)
        response = Response()
        tokens = get_tokens(user)
        if request.data["platform"] == "web":
            response.data = {"access": tokens["access"]}
            response.set_cookie(
                key="refresh",
                value=tokens["refresh"],
                httponly=True,
                samesite="None",
                secure=True,  # Use True in production with HTTPS
            )
        else:
            response.data = tokens
        return response


@method_decorator(gzip_page, name="dispatch")
class VerifyOTP(APIView):

    def post(self, request):
        try:
            serializer = VerifyAccountSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_if_exists(User, email=request.data["email"])
            if not user:
                return Response(
                    {
                        "msg": "Invalid user",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_token = OneTimePassword.objects.get(user=user)
            if serializer.data["otp"] != user_token.otp:
                return Response(
                    {
                        "msg": "Invalid otp",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            devices = get_if_exists(
                Devices, user=user, user_agent=request.META.get("HTTP_USER_AGENT")
            )
            if not devices:
                Devices.objects.create(
                    user=user,
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                    language=request.META.get("HTTP_ACCEPT_LANGUAGE", "en"),
                )

            user.is_verified = True
            user.save()
            return Response(get_tokens(user))
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class ResetPasswordAPI(APIView):
    def res(self, email):
        return Response(
            {
                "msg": f"If an account exists for {email}, you will receive an otp.",
            }
        )

    def post(self, request):
        user = get_if_exists(User, email=request.data["email"])
        if not user:
            return self.res(request.data["email"])

        user.is_verified = False
        user.save()
        HandleEmail.delay(user.id, user.email, user.first_name, "update")
        return self.res(request.data["email"])


@method_decorator(gzip_page, name="dispatch")
class ChangePasswordAPI(APIView):
    def error_msg(self):
        return {
            "msg": "Error, try again later",
        }

    def error_msg2(self):
        return {
            "msg": "Invalid otp",
        }

    def error_msg3(self):
        return {
            "msg": "Cannot use this password",
        }

    def post(self, request):
        try:
            user = get_if_exists(User, email=request.data["email"])
            if not user:
                return Response(
                    self.error_msg(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = OneTimePassword.objects.get(user=user)
            if token.otp != request.data["otp"]:
                return Response(
                    self.error_msg2(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if user.check_password(request.data["password"]):
                return Response(
                    self.error_msg3(),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            old_paswords = OldPassword.objects.filter(user=user)
            for old_pasword in old_paswords:
                if check_password(request.data["password"], old_pasword.password):
                    return Response(
                        self.error_msg3(),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            device = get_if_exists(
                Devices, user=user, user_agent=request.META.get("HTTP_USER_AGENT")
            )
            if not device:
                Devices.objects.create(
                    user=user,
                    user_agent=request.META.get("HTTP_USER_AGENT"),
                    language=request.META.get("HTTP_ACCEPT_LANGUAGE", "en"),
                )
            OldPassword.objects.create(user=user, password=user.password)
            user.set_password(request.data["password"])
            user.is_verified = True
            user.save()
            return Response({"msg": "ok"})
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class UserView(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)

            if not user:
                return Response(
                    {"msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # acc = get_if_exists(MT5Account, user=user)
            # if not acc:
            #     data = {}
            # else:
            #     data = MT5AccountSerializer(acc).data
            return Response(
                {
                    "data": UserSerializer(user).data,
                    # "trade_account_data": data,
                }
            )
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class UpdateUser(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def put(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)

            if not user:
                return Response(
                    {"msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.first_name = request.data.get("first_name", user.first_name)
            user.last_name = request.data.get("last_name", user.last_name)
            user.save()
            return Response(
                {
                    "data": UserSerializer(user).data,
                }
            )
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class LogoutAPIView(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = get_if_exists(User, id=request.user_id)
            device = get_if_exists(
                Notification_Devices, device_id=request["device_id"], user=user
            )

            if not user or not device:
                return Response(
                    {"msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            device.delete()
            return Response({"msg": "Logout Successful"})
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class Connect_MT5_Account(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            broker = get_if_exists(Brokers, id=request.data["server"])
            if not broker:
                return Response(
                    {"msg": "Broker does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not mt5.initialize():
                return Response(
                    {"msg": "Terminal Error"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            login_status = mt5.login(
                login=int(request.data["account"]),
                password=request.data["password"],
                server=broker.name,
            )

            if not login_status:
                return Response(
                    {"msg": "Trade account does not exist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            account = get_if_exists(MT5Account, user__id=request.user_id)
            if account:
                account.account = int(request.data["account"])
                account.password = request.data["password"]
                account.server = broker
                account.verified = True
                account.save()
            else:
                account = MT5Account.objects.create(
                    user_id=request.user_id,
                    account=int(request.data["account"]),
                    password=request.data["password"],
                    server=broker,
                    activate_automation=True,
                    verified=True,
                )
            mt5.shutdown()
            return Response({"data": MT5AccountSerializer(account).data})

        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class Activate_Automation(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            account = get_if_exists(MT5Account, user__id=request.user_id)

            # if account.verified

            if request.data["activate"] is True:
                result = signal_trade_task.delay(
                    account.user.id,
                    account.account,
                    account.password,
                    account.server,
                    account.pair,
                    account.group_name,
                )
                Trade_Task.objects.create(account=account, task_id=result.id)
                account.activate_automation = True
                account.save()

                return Response({"msg": "Activation success"})

            elif request.data["activate"] is False:
                task = get_if_exists(Trade_Task, account=account)
                print(task.task_id)
                # app.control.revoke(task.task_id, terminate=True)
                task.delete()
                account.activate_automation = False
                account.save()

                return Response({"msg": "De-activation success"})
            else:
                return Response(
                    {"msg": "Bad request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class Get_Broker_ServersAPI(APIView):
    def brokers_list(self):
        data = Brokers.objects.filter(active=True)
        serializer = BrokersSerializer(data, many=True)
        return serializer.data

    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        return Response({"data": self.brokers_list()})


# from django.views.generic import View
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# import asyncio
# from asgiref.sync import sync_to_async
# @method_decorator(csrf_exempt, name="dispatch")
# class SSE(View):
#     async def fetch_data(self, id, sleep):
#         await asyncio.sleep(sleep)
#         print(f"Coroutine {id} startin to fetch data.")

#         return {
#             "id": id,
#             "data": f"from coroutine {id}"
#         }

#     def get_data(self):
#         oo = User.objects.all()
#         seriallizer =UserSerializer(oo, many=True)
#         return seriallizer.data

#     async def post(self, request):
#         # headers = request.headers
#         # body = request.body
#         asyncio.gather(self.fetch_data(1, 1),
#                                  self.fetch_data(2, 2),
#                                  self.fetch_data(3, 10))
#         # result = await results
#         return JsonResponse({
#             "yoo": await sync_to_async(self.get_data)(),
#             # "2": result
#         })
