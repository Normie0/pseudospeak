import json

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from cryptography.fernet import Fernet
from django.conf import settings
from .models import Room, Message

f=Fernet(settings.ENCRYPT_KEY)

class ChatConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def generate_key():
        return Fernet.generate_key()

    @sync_to_async
    def encrypt_data(data, key):
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data)
        return encrypted_data

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self,code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message = data['message']
        username = data['username']
        room = data['room']
        profile_img=await self.get_profile_img(username)

        await self.save_message(username, room, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'profile_img':profile_img
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        profile_img= event['profile_img']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'profile_img':profile_img
        }))

    @sync_to_async
    def save_message(self, username, room, message):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)
        if message:
            message_bytes=message.encode('utf-8')
            encrypt_message= f.encrypt(message_bytes)
            print(encrypt_message)
            message_decoded=encrypt_message.decode('utf-8')
            Message.objects.create(user=user, room=room, content=message_decoded)

    @sync_to_async
    def get_profile_img(self,username):
        user=User.objects.get(username=username)
        return user.profile.profile_img.url


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data=json.loads(text_data)

        print(data)

        id=data['id']
        username=data['username']

        await self.add_user_room(username,id)

    @sync_to_async
    def add_user_room(self,username,id):
        user=User.objects.get(username=username)
        room=Room.objects.get(pk=id)
        room.users.add(user)
        room.save()
        print(room.users.all())