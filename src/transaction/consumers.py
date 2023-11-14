import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        self.group_name = f"user_{user.id}_transaction_notification"
        
        #join own group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def recieve(self, data):
        json_data = json.loads(data)
        await self.channel_layer.group_send(json_data)
    
    @database_sync_to_async
    def get_unread_notifications(self):
        return Notification.unreads.get_for_user(self.scope["user"].id).values_list("message", "created_at")
    
    async def notify(self, event):
        data = await self.get_unread_notifications()
        await self.send(text_data=json.dumps(data))
    