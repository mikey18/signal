from channels.db import database_sync_to_async
from fcm_django.models import FCMDevice
from firebase_admin.messaging import (Message, 
                                      Notification, 
                                      send)
from celery import shared_task

# def send_notification_sync(**kwargs):
#     try:
#         devices = FCMDevice.objects.filter(user_id=kwargs.get("user_id"), active=True)
#         if devices:
#             message_data = {
#                 # "badge": "",
#                 "title": kwargs.get("title", ""),
#                 "body": kwargs.get("body", ""),
#                 # "image": kwargs.get("image", ""),
#                 # "icon": kwargs.get("icon", ""),
#             }
#             message = Message(data=message_data)     
#             # for device in devices:
#             #     device.send_message(message)   
#             SENT = devices.send_message(message)   
#             print(SENT)
#     except Exception as e:
#         print(e)

@shared_task
def send_notification_sync(**kwargs):
    try:
        devices = FCMDevice.objects.filter(user_id=kwargs.get("user_id"), active=True)
        message_data = {
            "title":kwargs.get("title", ""),
            "body": kwargs.get("body", ""),
        }
        for device in devices:
            if device.type == 'web':
                msg = Message(
                    token=device.registration_id,
                    data=message_data
                )
            else:
                msg = Message(
                    token=device.registration_id,
                    notification=Notification(
                        **message_data
                    )
                )
            MSG = send(msg) 
            print(MSG)    
    except Exception as e:
        print(e)

@shared_task
async def send_notification_async(**kwargs):
    try:
        devices = await database_sync_to_async(list)(FCMDevice.objects.filter(user_id=kwargs.get("user_id"), active=True))
        if devices:
            message_data = {
                "title": kwargs.get("title", ""),
                "body": kwargs.get("body", ""),
            }
            # await asyncio.sleep(0.05)
            for device in devices:
                if device.type == 'web':
                    msg = Message(
                        token=device.registration_id,
                        data=message_data
                    )
                else:
                    msg = Message(
                        token=device.registration_id,
                        notification=Notification(
                            **message_data
                        )
                    )
                MSG = send(msg) 
                print(MSG)           
    except Exception as e:
        print(e)
