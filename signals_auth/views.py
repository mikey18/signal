from .models import User, MT5Account, Brokers
from Generate_signals.models import Trade_Task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (RegisterSerializer,
                          LoginSerializer, 
                          MT5AccountSerializer,
                          UserSerializer,
                          BrokersSerializer)
from datetime import datetime, timedelta, timezone
from .functions.auth_functions import auth_encoder, auth_decoder
from functions.CustomQuery import get_if_exists
from Generate_signals.tasks import signal_trade_task
import MetaTrader5 as mt5
from dotenv import load_dotenv
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
load_dotenv()
    
@method_decorator(gzip_page, name='dispatch')
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        users_count = User.objects.all().count()
        if users_count == 2:
            return Response({
                "status": 400,
                "message": "System only supports one user for now",
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": 200,
            "message": "Successful",
            "user": serializer.data
        })

@method_decorator(gzip_page, name='dispatch')
class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def get_token(self, user):
        payload = {
            "id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
            "iat": datetime.now(timezone.utc)
        }
        return auth_encoder(payload)
    
    def bad_response(self):
        return Response({
            "status": 400,
            "message": "Invalid email or password"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data["email"].lower(), is_active=True)
        except Exception:
            return self.bad_response()
        
        if not user.check_password(request.data["password"]) or user.is_superuser:
            return self.bad_response()

        return Response({
            "status": 200,
            "token": self.get_token(user)
        })
           
@method_decorator(gzip_page, name='dispatch')
class UserView(APIView):
    def get(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            user = get_if_exists(User, id=payload["id"])

            if not user:
                return Response({
                    "status": 400,
                    "msg": "Not Authorized"
                }, status=status.HTTP_400_BAD_REQUEST)
            acc = get_if_exists(MT5Account, user=user)
            if not acc:
                data = {}
            else:
                data = MT5AccountSerializer(acc).data
            return Response({
                "status": 200,
                "user_data": UserSerializer(user).data,
                "trade_account_data": data
            })
        except Exception:
            return Response({
                "status": 400,
                "msg": "Not Authorized"
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(gzip_page, name='dispatch')
class UpdateUser(APIView):
    def put(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            user = get_if_exists(User, id=payload["id"])

            if not user:
                return Response({
                    "status": 400,
                    "msg": "Not Authorized"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.first_name = request.data.get("first_name", user.first_name)
            user.last_name = request.data.get("last_name", user.last_name)
            user.save()
            return Response({
                "status": 200,
                "data": UserSerializer(user).data,
            })
        except Exception:
            return Response({
                "status": 400,
                "msg": "Not Authorized"
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(gzip_page, name='dispatch')
class LogoutAPIView(APIView):
    def post(self, request):
        payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
        user = User.objects.get(id=payload["id"])
        if user is None:
            return Response({
                "status": 400,
                "message": "Logout Unsuccessful",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": 200,
            "message": "Logout Successful",
        })

@method_decorator(gzip_page, name='dispatch')
class Connect_MT5_Account(APIView):  
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            broker = get_if_exists(Brokers, id=request.data["server"])
            if not broker:
                return Response({
                    "status": 400,
                    "msg": "Broker does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not mt5.initialize():
                return Response({
                    "status": 400,
                    "msg": "Terminal Error"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            login_status = mt5.login(login=int(request.data["account"]), 
                                     password=request.data["password"], 
                                     server=broker.name)
            
            if not login_status:
                return Response({
                    "status": 400,
                    "msg": "Trade account does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)

            account = get_if_exists(MT5Account, user__id=payload["id"])        
            if account:
                account.account = int(request.data["account"])
                account.password = request.data["password"]
                account.server = broker
                account.verified = True               
                account.save()
            else:      
                account = MT5Account.objects.create(
                    user_id=payload["id"],
                    account=int(request.data["account"]),
                    password=request.data["password"],
                    server=broker,
                    activate_automation=True,
                    verified = True,
                )
            mt5.shutdown()
            return Response({
                "status": 200,
                "data": MT5AccountSerializer(account).data
            })
    
        except Exception as e:
            print(e)
            return Response({
                "status": 400,
                "msg": "Not Authorized"
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(gzip_page, name='dispatch')
class Activate_Automation(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            account = get_if_exists(MT5Account, user__id=payload["id"])

            # if account.verified

            if request.data["activate"] is True:
                result = signal_trade_task.delay(
                                  account.user.id,
                                  account.account, 
                                  account.password, 
                                  account.server, 
                                  account.pair, 
                                  account.group_name)
                Trade_Task.objects.create(account=account, task_id=result.id)
                account.activate_automation = True
                account.save()

                return Response({
                    "status": 200,
                    "msg": "Activation success"
                })

            elif request.data["activate"] is False:
                task = get_if_exists(Trade_Task, account=account)
                print(task.task_id)
                # app.control.revoke(task.task_id, terminate=True)
                task.delete()
                account.activate_automation = False
                account.save()

                return Response({
                    "status": 200,
                    "msg": "De-activation success"
                })
            else:
                return Response({
                    "status": 400,
                    "msg": "Bad request"
                }, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(e)
            return Response({
                "status": 400,
                "msg": "Not Authorized"
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(gzip_page, name='dispatch')
class Get_Broker_ServersAPI(APIView):
    def brokers_list(self):
        data = Brokers.objects.filter(active=True)
        serializer = BrokersSerializer(data, many=True)
        return serializer.data
       
    def get(self, request):
        try:
            auth_decoder(request.META.get('HTTP_AUTHORIZATION'))
            return Response({
                'status': 200,
                'data': self.brokers_list()            
            })
        except Exception:
            return Response({
                "status": 400,
                "msg": 'Not Authorized'
            }, status=status.HTTP_400_BAD_REQUEST)


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