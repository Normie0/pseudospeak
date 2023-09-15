import json
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import TrendingMessage
from .models import Profile

class IndexConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        username = data['username']
        profile_img_url = await self.get_profile_img(username)
        print(data)
        await self.save_message(username, content)

        # Broadcast the received message to all connected clients
        await self.send_group_message(username,content,profile_img_url)

    @sync_to_async
    def get_profile_img(self, username):
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        return profile.profile_img.url

    @sync_to_async
    def save_message(self, username, message):
        user = User.objects.get(username=username)
        if message:
            TrendingMessage.objects.create(user=user, content=message)

    # Helper function to send a message to all clients in the same group
    async def send_group_message(self, username, content,profile_img_url):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send("index_group", {
            "type": "broadcast_message",
            "username": username,
            "content": content,
            "profile_img":profile_img_url
        })

    # Receive broadcasted message and send it to the WebSocket
    async def broadcast_message(self, event):
        username = event["username"]
        content = event["content"]
        profile_img=event["profile_img"]
        await self.send(text_data=json.dumps({
            'username': username,
            'content': content,
            'profile_img':profile_img
        }))
