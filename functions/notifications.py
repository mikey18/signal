from notification.models import Notification_Devices
from firebase_admin.messaging import Message, Notification, send
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_sync(**kwargs):
    try:
        message_data = {
            "title": kwargs.get("title", ""),
            "body": kwargs.get("body", ""),
        }

        if kwargs.get("type") == "web":
            msg = Message(token=kwargs.get("token"), data=message_data)
        else:
            msg = Message(
                token=kwargs.get("token"), notification=Notification(**message_data)
            )
        MSG = send(msg)
        logger.info(f"Success, {MSG}")
    except Exception as e:
        logger.info(e)
        device = Notification_Devices.objects.get(registration_id=kwargs.get("token"))
        logger.info("token is invalid, deleting from db")
        device.delete()


def PUSH_NOTIFICATION(**kwargs):
    devices = Notification_Devices.objects.filter(user__id=kwargs.get("user_id"))
    for device in devices:
        send_notification_sync.delay(
            title=kwargs.get("title"),
            body=kwargs.get("body"),
            type=device.type,
            token=device.registration_id,
        )


# @shared_task
# async def send_notification_async(**kwargs):
#     try:
#         devices = await database_sync_to_async(list)(Notification_Devices.objects.filter(user__id=kwargs.get("user_id")))
#         if devices:
#             message_data = {
#                 "title": kwargs.get("title", ""),
#                 "body": kwargs.get("body", ""),
#             }
#             # await asyncio.sleep(0.05)
#             for device in devices:
#                 if kwargs.get("type") == 'web':
#                     msg = Message(
#                         token=kwargs.get("token"),
#                         data=message_data
#                     )
#                 else:
#                     logger.info(device.device_id)
#                     msg = Message(
#                         token=kwargs.get("token"),
#                         notification=Notification(
#                             **message_data
#                         )
#                     )
#                 MSG = send(msg)
#                 logger.info(MSG)
#     except Exception as e:
#         logger.info(e)
