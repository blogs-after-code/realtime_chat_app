import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, UserStatus
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.accept()
            await self.update_user_status(True)
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.update_user_status(False)
    
    async def receive(self, text_data):
        pass
    
    @database_sync_to_async
    def update_user_status(self, is_online):
        status, created = UserStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.last_seen = timezone.now()
        status.save()