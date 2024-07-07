from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from fcm_django.models import FCMDevice
from functions.CustomQuery import get_if_exists
from signals_auth.functions.auth_functions import auth_decoder
from signals_auth.models import User
from functions.notifications import (send_notification_sync, 
                                    send_notification_async)
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
import json
import asyncio
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async


@method_decorator(gzip_page, name='dispatch')
class Register_Push_Notification(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get('HTTP_AUTHORIZATION'))
            user = get_if_exists(User, id=payload['id'])

            if not user:
                return Response({
                    "status": 400,
                    "msg": 'Not Authorized'
                }, status=status.HTTP_400_BAD_REQUEST)

            fcm = get_if_exists(FCMDevice,
                registration_id=request.data['token']
            )
            # this will replace details if the token already exists in the database
            fullname = f"{user.first_name} {user.last_name}"
            if fcm:
                fcm.name = fullname
                fcm.user_id = payload['id']
                fcm.save()
            else:
                # this will register new token with user
                FCMDevice.objects.create(
                    name=fullname,
                    user_id=payload['id'],
                    registration_id=request.data['token'],
                    type=request.data['type']
                )
            return Response({
                'status': 200
            })
        except Exception as e:
            print(e)
            return Response({
                "status": 400,
                "msg": 'Not Authorized'
            }, status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(gzip_page, name='dispatch')
class Test_Push_Notification_Sync(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META['HTTP_AUTHORIZATION'])
            user = get_if_exists(User, id=payload['id'])

            if not user:
                return Response({
                    "status": 400,
                    "msg": 'Not Authorized'
                }, status=status.HTTP_400_BAD_REQUEST)
            send_notification_sync(
                user_id=payload['id'],
                title=request.data['title'],
                body=request.data['body']
            )
            return Response({
                'status': 200
            })
        except Exception as e:
            print(e)
            return Response({
                "status": 400,
                "msg": 'Not Authorized'
            }, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class Test_Push_Notification_Async(View):
    async def kk(self):
        for i in range(100): 
            print(i)
            await asyncio.sleep(1)

    async def post(self, request):
        try:
            payload = await sync_to_async(auth_decoder)(request.headers['Authorization'])
            user = await database_sync_to_async(User.objects.get)(id=payload['id'])
            body = json.loads(request.body)

            if not user:
                return JsonResponse({
                    "status": 400,
                    "msg": 'Not Authorized'
                }, status=HttpResponseBadRequest)
            
            asyncio.create_task(send_notification_async(
                user_id=payload['id'],
                title=body['title'],
                body=body['body']
            ))
            # asyncio.create_task(self.kk())
            return JsonResponse({
                'status': 200,
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "status": 400,
                "msg": 'Not Authorized'
            }, status=HttpResponseBadRequest)