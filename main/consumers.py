from django.core.files.base import ContentFile
import base64
import json
import os
from django.conf import settings
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.urls import reverse
from .models import TrendingMessage,Hashtag
from .models import Profile
from django.db.models import F
import re,time
from django.core.files.storage import default_storage
from django.conf import settings
from cryptography.fernet import Fernet

f=Fernet(settings.ENCRYPT_KEY)

def save_image(image_data, username):
    # Remove the part of the image_data that indicates the encoding
    format, imgstr = image_data.split(';base64,') 
    # Find out the file format (jpeg, png)
    ext = format.split('/')[-1] 
    print(imgstr)

    # Generate a filename
    filename = f"{username}_{time.time()}.{ext}"

    # Convert the base64 string to a ContentFile
    data = ContentFile(base64.b64decode(imgstr), name=filename)

    # Save the file
    file = default_storage.save(os.path.join("images", filename), data)

    # Return the relative file path
    return file


@sync_to_async
def like_message(like_id,username):
    message = TrendingMessage.objects.get(pk=like_id)
    user=User.objects.get(username=username)
    if user in message.userLiked.all():
        message.likes-=1
        message.userLiked.remove(user)
        message.save()
    else:
        message.likes += 1
        message.userLiked.add(user)
        message.save()
    return message.likes

@sync_to_async
def get_count(msgId,username):
    message = TrendingMessage.objects.get(pk=msgId)
    user=User.objects.get(username=username)
    if user not in message.viewed.all():
        message.view_count += 1
        message.viewed.add(user)
        message.save()
    return message.view_count



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

        elif 'likeId' in data:
            print(data['likeId'])
            likeId=data['likeId']
            username=data['username']
            likes=await like_message(data['likeId'],username)
            print(likes)
            await self.send_likes(likeId,likes)

        elif 'msgId' in data:
            print(data['msgId'])
            msgId=data['msgId']
            username=data['username']
            views=await get_count(msgId,username)
            await self.send_count(msgId,views)

        else:
            content = data['content']
            username = data['username']
            image=data['image']

            profile_img_url = await self.get_profile_img(username)

            print(data)

            hashtag = await self.hashtag_identifier(content)

            contentId=await self.save_message(username, content, hashtag, image)

            # Broadcast the received message to all connected clients
            await self.send_group_message(username,content,contentId,profile_img_url,hashtag,image)

    @sync_to_async
    def get_profile_img(self,username):
        user=User.objects.get(username=username)
        profile=Profile.objects.get(user=user)
        return profile.profile_img.url

    @sync_to_async
    def like_message(self,like_id):
        message = TrendingMessage.objects.get(pk=like_id)
        message.likes += 1
        message.save()
        
    @sync_to_async
    def get_hashtags(self,hashtag_name):
        return list(Hashtag.objects.filter(tag__icontains=hashtag_name).values_list('tag', flat=True))

    @sync_to_async
    def save_message(self, username, message, hashtag, image):
        user = User.objects.get(username=username)

        if image:
            # If there's image data, save it and get the file path
            image_file_path = save_image(image, username)
            image_url = settings.MEDIA_URL + image_file_path
        else:
            image_file_path = None

        if message:
            message_bytes=message.encode('utf-8')
            message_encrypted=f.encrypt(message_bytes)
            message_decoded=message_encrypted.decode('utf-8')
            # If there's message content, create the TrendingMessage object
            recentMessage=TrendingMessage.objects.create(
                user=user,
                content=message_decoded,
                image=image_file_path,  # Pass the file path of the saved image
            )

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
                hashtag=Hashtag.objects.get(tag=tag)
                recentMessage.hashtags.add(hashtag)
        
        return recentMessage.pk
                    


    @sync_to_async
    def hashtag_identifier(self,content):
        hashtag_pattern=re.compile(r'#\w+')
        hashtags=hashtag_pattern.findall(content)
        return hashtags

    # Helper function to send a message to all clients in the same group
    async def send_group_message(self, username, content,contentId,profile_img_url,hashtag,image):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send("index_group", {
            "type": "broadcast_message",
            "username": username,
            "content": content,
            "profile_img":profile_img_url,
            "hashtag":hashtag,
            "image":image,
            "contentId":contentId
        })

    # Receive broadcasted message and send it to the WebSocket
    async def broadcast_message(self, event):
        username = event["username"]
        content = event["content"]
        profile_img=event["profile_img"]
        hashtag=event["hashtag"]
        image=event["image"]
        contentId=event["contentId"]
        await self.send(text_data=json.dumps({
            'username': username,
            'content': content,
            'profile_img':profile_img,
            'hashtag':hashtag,
            'image':image,
            'contentId':contentId
        }))


    async def send_likes(self, likeId, likes):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send("index_group", {
            "type": "broadcast_likes",
            "likeId":likeId,
            "likes":likes,
        })

    async def broadcast_likes(self, event):
        likeId = event["likeId"]
        likes = event["likes"]
        await self.send(text_data=json.dumps({
            'likeId': likeId,
            'likes': likes,
        }))

    async def send_count(self, msgId, views):
        print("sending",views)
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send("index_group", {
            "type": "broadcast_views",
            "msgId":msgId,
            "views":views,
        })

    async def broadcast_views(self, event):
        msgId = event["msgId"]
        views = event["views"]
        await self.send(text_data=json.dumps({
            'msgId': msgId,
            'views': views,
        }))
