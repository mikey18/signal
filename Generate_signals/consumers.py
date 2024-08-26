import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from signals_auth.utils.auth_utils import auth_decoder, jwt_required_ws
from signals_auth.models import User, MT5Account, MT5Account_Symbols
from utils.CustomQuery import get_if_exists
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class PremiumCheckConsumer_Free(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = None
        token = self.scope["query_string"].decode("utf-8")
        self.payload = jwt_required_ws(token, "access")
        self.master = None
        if self.payload:
            user = await sync_to_async(get_if_exists)(
                User, id=self.payload["id"], is_verified=True
            )
            self.master = await sync_to_async(get_if_exists)(
                MT5Account, master=True, verified=True
            )
            if user and self.master:
                self.task_running = False
                await self.accept()

    async def disconnect(self, close_code):
        if self.master:
            await self.leave_rooms()
        if not self.payload:
            print("Token Invalid")

    async def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            if client_data["msg"] == "ping":
                if self.task_running:
                    await self.send(text_data=json.dumps({"status": False}))
                else:
                    master_symbols = await self.get_master_symbols()
                    async for symbol in master_symbols:
                        await self.channel_layer.group_add(
                            symbol.group_name, self.channel_name
                        )
                    self.task_running = True

                    symbols = []
                    for i in master_symbols:
                        symbols.append(i.pair)

                    await self.send(
                        text_data=json.dumps(
                            {
                                "status": True,
                                "message": "You are now receiving messages",
                                "symbols": symbols,
                            }
                        )
                    )
            elif client_data["msg"] == "stop":
                if self.task_running:
                    await self.leave_rooms()
                    self.task_running = False
                    await self.send(
                        text_data=json.dumps({"status": True, "message": "Stopped"})
                    )
                else:
                    await self.send(text_data=json.dumps({"status": False}))
            else:
                await self.send(text_data=json.dumps({"status": False}))
                await self.close()
        except Exception:
            await self.close()

    async def leave_rooms(self):
        master_symbols = await self.get_master_symbols()
        async for symbol in master_symbols:
            await self.channel_layer.group_discard(symbol.group_name, self.channel_name)

    async def get_master_symbols(self):
        return await database_sync_to_async(MT5Account_Symbols.objects.filter)(
            account=self.master, active=True
        )

    async def trade_format(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "message": event["message"],
                    "data": event["data"],
                }
            )
        )


class PremiumCheckConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = None
        token = self.scope["query_string"].decode("utf-8")
        self.payload = auth_decoder(token)
        user = await sync_to_async(get_if_exists)(User, id=self.payload["id"])
        account = await sync_to_async(get_if_exists)(
            MT5Account, user=user, verified=True
        )
        self.master = await sync_to_async(get_if_exists)(
            MT5Account, master=True, verified=True
        )
        if user and account and self.master:
            self.task_running = False
            await self.accept()

    async def disconnect(self, close_code):
        await self.leave_rooms()

    async def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            if client_data["msg"] == "ping":
                if self.task_running:
                    await self.send(text_data=json.dumps({"status": False}))
                else:
                    master_symbols = await self.get_master_symbols()
                    async for symbol in master_symbols:
                        await self.channel_layer.group_add(
                            symbol.group_name, self.channel_name
                        )
                    self.task_running = True

                    symbols = []
                    for i in master_symbols:
                        symbols.append(i.pair)

                    await self.send(
                        text_data=json.dumps(
                            {
                                "status": True,
                                "message": "You are now receiving messages",
                                "symbols": symbols,
                            }
                        )
                    )
            elif client_data["msg"] == "stop":
                if self.task_running:
                    await self.leave_rooms()
                    self.task_running = False
                    await self.send(
                        text_data=json.dumps({"status": True, "message": "Stopped"})
                    )
                else:
                    await self.send(text_data=json.dumps({"status": False}))
            else:
                await self.send(text_data=json.dumps({"status": False}))
                await self.close()
        except Exception:
            await self.close()

    async def leave_rooms(self):
        master_symbols = await self.get_master_symbols()
        async for symbol in master_symbols:
            await self.channel_layer.group_discard(symbol.group_name, self.channel_name)

    async def get_master_symbols(self):
        return await database_sync_to_async(MT5Account_Symbols.objects.filter)(
            account=self.master, active=True
        )

    async def trade_format(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "status": event["status"],
                    "message": event["message"],
                    "data": event["data"],
                }
            )
        )
