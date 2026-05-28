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
            self.room_group_name = f'user_{self.user.id}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            await self.update_user_status(True)
            await self.broadcast_user_status()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.update_user_status(False)
            await self.broadcast_user_status()
            
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            content = data['content']
            receiver_id = data.get('receiver_id')
            
            if receiver_id:
                receiver = await self.get_user(receiver_id)
                if receiver:
                    message = await self.save_message(self.user, receiver, content)
                    
                    await self.channel_layer.group_send(
                        f'user_{receiver_id}',
                        {
                            'type': 'chat_message',
                            'message': content,
                            'sender': self.user.username,
                            'sender_id': self.user.id,
                            'timestamp': message.timestamp.isoformat()
                        }
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'message_sent',
                        'content': content,
                        'receiver_id': receiver_id,
                        'timestamp': message.timestamp.isoformat()
                    }))
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'content': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))
    
    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user_id': event['user_id'],
            'is_online': event['is_online']
        }))
    
    async def broadcast_user_status(self):
        online_users = await self.get_online_users()
        for user_id in online_users:
            await self.channel_layer.group_send(
                f'user_{user_id}',
                {
                    'type': 'status_update',
                    'user_id': self.user.id,
                    'is_online': self.user.status.is_online if hasattr(self.user, 'status') else True
                }
            )
    
    @database_sync_to_async
    def update_user_status(self, is_online):
        status, created = UserStatus.objects.get_or_create(user=self.user)
        status.is_online = is_online
        status.last_seen = timezone.now()
        status.save()
    
    @database_sync_to_async
    def get_online_users(self):
        return list(UserStatus.objects.filter(is_online=True).values_list('user_id', flat=True))
    
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )