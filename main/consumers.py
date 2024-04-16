from datetime import datetime, timezone
import logging
from django.core.files.base import ContentFile
import base64
import json
import os
from django.conf import settings
from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.urls import reverse
from .models import TrendingMessage, Hashtag,Notification
from .models import Profile
from django.db.models import F
import re, time
from django.core.files.storage import default_storage
from django.conf import settings
from cryptography.fernet import Fernet
from conversation.models import Conversation, ConversationMessage
from django.db.models import Q

f = Fernet(settings.ENCRYPT_KEY)


def save_image(image_data, username):
    # Remove the part of the image_data that indicates the encoding
    format, imgstr = image_data.split(";base64,")
    # Find out the file format (jpeg, png)
    ext = format.split("/")[-1]
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
def like_message(like_id, username):
    message = TrendingMessage.objects.get(pk=like_id)
    user = User.objects.get(username=username)
    if user in message.userLiked.all():
        message.likes -= 1
        message.userLiked.remove(user)
        message.save()
    else:
        message.likes += 1
        message.userLiked.add(user)
        message.save()
    return message.likes


@sync_to_async
def get_count(msgId, username):
    message = TrendingMessage.objects.get(pk=msgId)
    user = User.objects.get(username=username)
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

        if "question" in data:
            messageId,profile_img_url=await self.save_poll(data)
            await self.send_poll_message(data['username'],data['question'],messageId,profile_img_url,data['option1'],data['option2'])

        elif "selected" in data:
                # Call the function to update the option counts based on the selected option
            option1_count, option2_count, mId,option1,option2 = await self.select_option(data)
            # Send the updated option counts back to the client
            print(option1_count,option2_count,mId,option1,option2)
            await self.send(text_data=json.dumps({
                    "option1_count": option1_count,
                    "option2_count": option2_count,
                    "mId":mId,
                    "option1":option1,
                    "option2":option2,
                    "confirm":"pollConfirm"
                }))

        elif "hashtag" in data:
            print(data["hashtag"])
            hashtag = data["hashtag"]
            hashtag_list = await self.get_hashtags(hashtag)
            await self.send(text_data=json.dumps({"hashtags": hashtag_list}))

        elif "blockuser" in data:
            print(data)
            await self.block_user(data)

        elif "likeId" in data:
            print(data["likeId"])
            likeId = data["likeId"]
            username = data["username"]
            likes = await like_message(data["likeId"], username)
            print(likes)
            await self.send_likes(likeId, likes)

        elif "msgId" in data:
            print(data["msgId"])
            msgId = data["msgId"]
            username = data["username"]
            views = await get_count(msgId, username)
            await self.send_count(msgId, views)

        elif "ping" in data:
            print("pong")

        else:
            content = data["content"]
            username = data["username"]
            image = data["image"]

            profile_img_url = await self.get_profile_img(username)

            print(data)

            hashtag = await self.hashtag_identifier(content)

            contentId = await self.save_message(username, content, hashtag, image)

            # Broadcast the received message to all connected clients
            await self.send_group_message(
                username, content, contentId, profile_img_url, hashtag, image
            )

    @sync_to_async
    def save_poll(self,data):
        user=User.objects.get(username=data['username'])
        message_bytes = data['question'].encode("utf-8")
        message_encrypted = f.encrypt(message_bytes)
        message_decoded = message_encrypted.decode("utf-8")
        poll=TrendingMessage.objects.create(user=user,content=message_decoded,option1=data['option1'],option2=data['option2'])
        return poll.pk,user.profile.profile_img.url
        
    @sync_to_async
    def select_option(self,data):
        user=User.objects.get(username=data["username"])
        message=TrendingMessage.objects.get(pk=data['messageId'])
        message.voted.add(user)
        if (data['selected']==message.option1):
            message.votes_option1+=1
        elif (data['selected']==message.option2):
            message.votes_option2+=1
        message.view_count+=1
        message.viewed.add(user)
        message.save()
        print(data['selected'])
        option1_count=message.option1_count()
        option2_count=message.option2_count()

        return option1_count,option2_count,message.pk,message.option1,message.option2

    async def send_poll_message(
        self, username, content, contentId, profile_img_url,option1,option2,confirm="pollConfirm"
    ):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send(
            "index_group",
            {
                "type": "poll_message",
                "username": username,
                "content": content,
                "profile_img": profile_img_url,
                "contentId": contentId,
                "choice1":option1,
                "choice2":option2,
                "confirm":confirm
            },
        )

    async def poll_message(self, event):
        username = event["username"]
        content = event["content"]
        profile_img = event["profile_img"]
        contentId = event["contentId"]
        choice1=event["choice1"]
        choice2=event["choice2"]
        confirm=event["confirm"]
        await self.send(
            text_data=json.dumps(
                {
                    "username": username,
                    "content": content,
                    "profile_img": profile_img,
                    "contentId": contentId,
                    "choice1":choice1,
                    "choice2":choice2,
                    "confimr":confirm
                }
            )
        )


    @sync_to_async
    def block_user(self,data):
        user_to_block=User.objects.get(username=data['blockuser'])
        user=User.objects.get(username=data['username'])
        user.profile.blocked_user.add(user_to_block)
        user.profile.follow.remove(user_to_block)
        user.profile.following.remove(user_to_block)
        user_to_block.profile.blocked_user.add(user)
        user_to_block.save()
        user.save()

    @sync_to_async
    def get_profile_img(self, username):
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        return profile.profile_img.url

    @sync_to_async
    def like_message(self, like_id):
        message = TrendingMessage.objects.get(pk=like_id)
        message.likes += 1
        message.save()

    @sync_to_async
    def get_hashtags(self, hashtag_name):
        return list(
            Hashtag.objects.filter(tag__icontains=hashtag_name).values_list(
                "tag", flat=True
            )
        )

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
            message_bytes = message.encode("utf-8")
            message_encrypted = f.encrypt(message_bytes)
            message_decoded = message_encrypted.decode("utf-8")
            # If there's message content, create the TrendingMessage object
            recentMessage = TrendingMessage.objects.create(
                user=user,
                content=message_decoded,
                image=image_file_path,  # Pass the file path of the saved image
            )

            for tag in hashtag:
                try:
                    # Try to get the existing Hashtag object
                    hashtag = Hashtag.objects.get(tag=tag)

                    # Increment the count using F expression
                    hashtag.count = F("count") + 1
                    hashtag.save()
                except:
                    # If the hashtag doesn't exist, create it with a count of 1
                    Hashtag.objects.create(tag=tag, count=1)
                hashtag = Hashtag.objects.get(tag=tag)
                recentMessage.hashtags.add(hashtag)

        return recentMessage.pk

    @sync_to_async
    def hashtag_identifier(self, content):
        hashtag_pattern = re.compile(r"#\w+")
        hashtags = hashtag_pattern.findall(content)
        return hashtags

    # Helper function to send a message to all clients in the same group
    async def send_group_message(
        self, username, content, contentId, profile_img_url, hashtag, image
    ):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send(
            "index_group",
            {
                "type": "broadcast_message",
                "username": username,
                "content": content,
                "profile_img": profile_img_url,
                "hashtag": hashtag,
                "image": image,
                "contentId": contentId,
            },
        )

    # Receive broadcasted message and send it to the WebSocket
    async def broadcast_message(self, event):
        username = event["username"]
        content = event["content"]
        profile_img = event["profile_img"]
        hashtag = event["hashtag"]
        image = event["image"]
        contentId = event["contentId"]
        await self.send(
            text_data=json.dumps(
                {
                    "username": username,
                    "content": content,
                    "profile_img": profile_img,
                    "hashtag": hashtag,
                    "image": image,
                    "contentId": contentId,
                }
            )
        )
        print("Image message")

    async def send_likes(self, likeId, likes):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send(
            "index_group",
            {
                "type": "broadcast_likes",
                "likeId": likeId,
                "likes": likes,
            },
        )

    async def broadcast_likes(self, event):
        likeId = event["likeId"]
        likes = event["likes"]
        await self.send(
            text_data=json.dumps(
                {
                    "likeId": likeId,
                    "likes": likes,
                }
            )
        )

    async def send_count(self, msgId, views):
        print("sending", views)
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send(
            "index_group",
            {
                "type": "broadcast_views",
                "msgId": msgId,
                "views": views,
            },
        )

    async def broadcast_views(self, event):
        msgId = event["msgId"]
        views = event["views"]
        await self.send(
            text_data=json.dumps(
                {
                    "msgId": msgId,
                    "views": views,
                }
            )
        )


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if 'changedName' in data:
            print("Event running")
            error_message=await self.changename(data)
            
            await self.send(text_data=json.dumps({
            "error_message":error_message,
            "changedame":data['changedName']
            }))
            
        else:
            await self.follow(data)

    @sync_to_async
    def changename(self,data):
        try:
            user=User.objects.get(username=data['username'])
            user.username=data['changedName']
            user.save()
            print(user.username)
            return None
        except:
            error_message="username already in use"
            return error_message
            

    @sync_to_async
    def follow(self, data):
        user = User.objects.get(username=data["username"])
        loggeduser = User.objects.get(username=data["loggedusername"])

        if data["followStatus"] == "Unfollow":
            user.profile.follow.remove(loggeduser)
            loggeduser.profile.following.remove(user)

        else:
            user.profile.follow.add(loggeduser)
            loggeduser.profile.following.add(user)
            conversation = Conversation.objects.filter(members=user).filter(
                members=loggeduser
            )
            if not conversation.exists():
                conversation = Conversation.objects.create()
                conversation.members.add(loggeduser)
                conversation.members.add(user)


class MessengerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data=json.loads(text_data)
        print(data)
        conversation_list=await self.fetchconversation(data)
        
        await self.send(text_data=json.dumps({
            'conversations':conversation_list
        }))

    @sync_to_async
    def fetchconversation(self,data):
        username_with_comma=data['username']
        username=username_with_comma.replace('"','')
        user=User.objects.get(username=username)
        users=User.objects.filter(username__startswith=data['searchTxt'])

        conversations=[]
        for user2 in users:
            conversations+=Conversation.objects.filter(members=user).filter(members=user2)
        
        conversation_list=[]
        for conv in conversations:
            members = conv.members.exclude(username=user.username)
            member_details = [{'id': member.pk, 'username': member.username, 'profile_img': member.profile.profile_img.url} for member in members]


            conversation_list.append({
                'id': conv.id,
                'members': member_details,
                # Add other conversation fields as needed
            })
        print(conversation_list)
        return conversation_list


class ConversationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["id"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        username,img_url=await self.saveconversation(data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.content',  # Specify the type attribute
                'content': data['content'],
                'username': username,
                'id': data['id'],
                'img_url': img_url
            }
        )

    async def chat_content(self, event):
        # Handle the incoming message
        await self.send(text_data=json.dumps({
            'type': 'chat.content',
            'content': event['content'],
            'username': event['username'],
            'id': event['id'],
            'img_url': event['img_url'],
        }))

    @sync_to_async
    def saveconversation(self,data):
        username_with_strip=data['username']
        username=username_with_strip.replace('"','')
        print(username)
        user=User.objects.get(username=username)
        img_url=user.profile.profile_img.url
        conversation=Conversation.objects.get(pk=data['id'])
        message_bytes=data['content'].encode('utf-8')
        encrypt_message= f.encrypt(message_bytes)
        print(encrypt_message)
        message_decoded=encrypt_message.decode('utf-8')
        conversation_message=ConversationMessage.objects.create(conversation=conversation,content=message_decoded,created_by=user,)
        conversation.modified_at=datetime.now
        conversation.save()
        
        return username,img_url


class ReplyConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):

        data=json.loads(text_data)
        print(data)

        if 'likeId' in data:
            print("success")
            likecount=await self.like_message(data)
            await self.send_likes(
                likecount,data['likeId']
            )

        else:
            img_url,username,messageId=await self.save_reply(data)
            await self.send_group_message(
                username,img_url,data['content'],messageId,
            )

    @sync_to_async
    def like_message(self,data):
        username=data['username'].replace('"','')
        user=User.objects.get(username=username)
        message=TrendingMessage.objects.get(pk=data['likeId'])
        if user in message.userLiked.all():
            message.likes -= 1
            message.userLiked.remove(user)
            message.save()
        else:
            message.likes += 1
            message.userLiked.add(user)
            message.save()
        return message.likes
        
    
    async def send_likes(
            self,likecount,messageId
    ):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send(
            "index_group",
            {
                "type":"broadcast_likes",
                "likecount":likecount,
                "messageId":messageId
            }
        )

    async def broadcast_likes(self,event):
        likecount=event['likecount']
        messageId=event['messageId']
        await self.send(
            text_data=json.dumps({
                "likecount":likecount,
                "likeId":messageId
            })
        )


    async def send_group_message(
        self, username, img_url, content,messageId
    ):
        await self.channel_layer.group_add("index_group", self.channel_name)
        await self.channel_layer.group_send(
            "index_group",
            {
                "type": "broadcast_message",
                "username": username,
                "content": content,
                "profile_img": img_url,
                "messageId":messageId
            },
        )

    # Receive broadcasted message and send it to the WebSocket
    async def broadcast_message(self, event):
        username = event["username"]
        content = event["content"]
        profile_img = event["profile_img"]
        messageId=event["messageId"]
        await self.send(
            text_data=json.dumps(
                {
                    "username": username,
                    "content": content,
                    "profile_img": profile_img,
                    "messageId":messageId
                }
            )
        )


    @sync_to_async
    def save_reply(self,data):
        username=data['username'].replace('"','')
        user=User.objects.get(username=username)
        message=TrendingMessage.objects.get(pk=data['messageId'])
        message_bytes=data['content'].encode('utf-8')
        encrypt_message= f.encrypt(message_bytes)
        print(encrypt_message)
        message_decoded=encrypt_message.decode('utf-8')
        reply_message=TrendingMessage.objects.create(user=user,parent_message=message,content=message_decoded)
        print(reply_message.decrypt_message())
        return user.profile.profile_img.url,username,reply_message.pk
        

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notification_group", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data):
        data=json.loads(text_data)
        if 'notification_id' in data:
            print(data)
            await self.modify_notification(data['notification_id'])
        elif 'username' in data:
            touser=await self.save_notification(data)
            notification_message = f"You received a new message from {data['username']}"
            await self.broadcast_notification(touser.username, notification_message,data['id'])
        
        

    async def broadcast_notification(self, touser, message,id):
    # Add the consumer's channel to the group

        # Broadcast the message to all consumers in the group
        await self.channel_layer.group_send(
            "notification_group",
            {
                "type": "send_notification",
                "touser": touser,
                "message": message,
                "id":id,
            },

        )

    async def send_notification(self, event):
        touser = event["touser"]
        message = event["message"]
        id=event["id"]

        # Send the notification to the consumer
        await self.send(text_data=json.dumps({
            "touser": touser,
            "message": message,
            "id":id,
        }))

        print("Success")


    @sync_to_async
    def save_notification(self,data):
        username = data.get('username', '')  # Get the value of 'username' or default to an empty string if key is not found
        # Remove unwanted characters (e.g., double quotes) from the 'username' value
        sanitized_username = username.replace('"', '')
        user=User.objects.get(username=sanitized_username)
        conversation=Conversation.objects.get(pk=data['id'])
        for m in conversation.members.all():
            if m!=user:
                touser=m
                notification=Notification.objects.create(user=m,conversation=conversation,content=f"You received a new message from {sanitized_username}")
                notification.save()
        return touser
    
    @sync_to_async
    def modify_notification(self,id):
        notification=Notification.objects.get(pk=id)
        notification.seen=True
        notification.save()
        
        