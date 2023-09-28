import json
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import TrendingMessage,Hashtag
from .models import Profile
from django.db.models import F
import re

class IndexConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        if 'hashtag' in data:
            print(data['hashtag'])
            hashtag=data['hashtag']
            hashtag_list = await self.get_hashtags(hashtag)
            await self.send(text_data=json.dumps({
                'hashtags':hashtag_list
            }))
        else:
            content = data['content']
            username = data['username']
            profile_img_url = await self.get_profile_img(username)
            print(data)

            hashtag = await self.hashtag_identifier(content)

            await self.save_message(username, content,hashtag)

            # Broadcast the received message to all connected clients
            await self.send_group_message(username,content,profile_img_url,hashtag)
        
    @sync_to_async
    def get_hashtags(self,hashtag_name):
        return list(Hashtag.objects.filter(tag__icontains=hashtag_name).values_list('tag', flat=True))


    @sync_to_async
    def get_profile_img(self, username):
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        return profile.profile_img.url

    @sync_to_async
    def save_message(self, username, message,hashtag):
        user = User.objects.get(username=username)
        if message:
            TrendingMessage.objects.create(user=user, content=message)
            for tag in hashtag:
                try:
                    # Try to get the existing Hashtag object
                    hashtag = Hashtag.objects.get(tag=tag)

                    # Increment the count using F expression
                    hashtag.count = F('count') + 1
                    hashtag.save()
                except:
                    # If the hashtag doesn't exist, create it with a count of 1
                    Hashtag.objects.create(tag=tag, count=1)

    @sync_to_async
    def hashtag_identifier(self,content):
        hashtag_pattern=re.compile(r'#\w+')
        hashtags=hashtag_pattern.findall(content)
        return hashtags

    # Helper function to send a message to all clients in the same group
    async def send_group_message(self, username, content,profile_img_url,hashtag):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send("index_group", {
            "type": "broadcast_message",
            "username": username,
            "content": content,
            "profile_img":profile_img_url,
            "hashtag":hashtag,
        })

    # Receive broadcasted message and send it to the WebSocket
    async def broadcast_message(self, event):
        username = event["username"]
        content = event["content"]
        profile_img=event["profile_img"]
        hashtag=event["hashtag"]
        await self.send(text_data=json.dumps({
            'username': username,
            'content': content,
            'profile_img':profile_img,
            'hashtag':hashtag
        }))
