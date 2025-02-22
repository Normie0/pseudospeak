from io import BytesIO
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from faker import Faker
import urllib3
from .forms import *
import random
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile, TrendingMessage, Hashtag,ReportUser,Notification
from django.db.models import Sum, OuterRef
from conversation.models import Conversation, ConversationMessage
import base64

def generate_unique_username():
    fake = Faker()

    while True:
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            return username


def get_random_image():
    images = [
        "images/bear.png",
        "images/boy.png",
        "images/cat.png",
        "images/chicken.png",
        "images/dog.png",
        "images/dinosaur.png",
        "images/hacker.png",
        "images/panda.png",
    ]
    return random.choice(images)

from django.db.models import Count
@login_required(login_url="login_or_signup_view")
# Create your views here.
def index(request):
    blocked_users = request.user.profile.blocked_user.all()
    messages = TrendingMessage.objects.filter(
    parent_message=None
).exclude(
    user__in=blocked_users
).order_by("-custom_ordering")
    
    notifactions=Notification.objects.filter(user=request.user,seen=False)

    popular_users = User.objects.annotate(follow_count=Count('following')).order_by('-follow_count')[:3]
    
    hashtags = Hashtag.objects.all()[:3]
    if request.method=='POST':
        reason=request.POST.get("reason")
        username=request.POST.get("userToReport")
        additionalInfo=request.POST.get("additionalInfo")
        print(username,reason,additionalInfo)
        if username and reason:
            user=User.objects.get(username=username)
            reportUser=ReportUser.objects.create(user=user,reason=reason,additionalInfo=additionalInfo)
            reportUser.save()
            error_message="User Reported Successfully"
            return render(
        request, "main/index.html", {"messages": messages,"error_message": error_message,"category":"success","hashtags": hashtags,"popular_users":popular_users}

    )
        
    return render(
        request, "main/index.html", {"messages": messages, "hashtags": hashtags,"popular_users":popular_users,"notifications":len(notifactions)}
    )


def hashtagMessages(request, hashtag):
    tag = f"#{hashtag}"
    blocked_users = request.user.profile.blocked_user.all()
    try:
        hashtag = Hashtag.objects.get(tag=tag)
    except Hashtag.DoesNotExist:
        hashtag = None
    messages = TrendingMessage.objects.filter(parent_message=None, hashtags=hashtag).exclude(
    user__in=blocked_users).order_by("-custom_ordering")
    hashtags = Hashtag.objects.all()[:3]
    popular_users = User.objects.annotate(follow_count=Count('following')).order_by('-follow_count')[:3]
    return render(
        request,
        "main/hashtagMessages.html",
        {"hashtag": hashtag, "messages": messages, "hashtags": hashtags,"popular_users":popular_users},
    )


def login_or_signup_view(request):
    username = generate_unique_username()
    if request.method == "POST":
        action = request.POST.get("action")
        print(action)

        if action == "signup":
            error_message = None
            username = request.POST.get("username")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            try:
                if confirm_password != password:
                    raise ValueError("Passwords do not match!")
                for char in password:
                    if char.isupper():
                        break
                    elif password.index(char) != len(password) - 1:
                        continue
                    raise ValidationError("Atleast one uppercase character is required")
                validate_password(password=password, password_validators=None)
            except ValueError as v:
                error_message = v
            except ValidationError as e:
                error_message = e.messages[:1]
                error_message = " ".join(error_message)
            try:
                existing_user = User.objects.get(username=username)
            except User.DoesNotExist:
                existing_user = None

            if existing_user is None and error_message is None:
                try:

                    if confirm_password == password and existing_user is None:
                        # Create the user first
                        create_user = User.objects.create_user(
                            username=username, password=password
                        )
                        random_image_path = get_random_image()

                        # Create the user's profile with the random image
                        profile = Profile(
                            user=create_user,
                            profile_img=random_image_path,
                            bio="New User",
                        )
                        print("completed registering user")
                        profile.save()
                        login(request, create_user)
                        return redirect("index")

                except ValidationError as e:
                    error_message = e.messages[:1]
                    error_message = " ".join(error_message)
                    return render(
                        request,
                        "main/signup.html",
                        {"error_message": error_message, "username": username},
                    )
            else:
                if existing_user is not None:
                    error_message = f"user with username {username} already exists! try using different username"
                return render(
                    request,
                    "main/signup.html",
                    {"error_message": error_message, "username": username},
                )

        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            print("This is a login action")
            user = authenticate(request, username=username, password=password)
            print(user)

            if user:
                login(request, user)
                return redirect("index")
            else:
                return render(
                    request,
                    "main/signup.html",
                    {
                        "error_message": "Invalid username or password",
                        "username": username,
                    },
                )
    return render(request, "main/signup.html", {"username": username})


def logoutuser(request):
    logout(request)
    return redirect("login_or_signup_view")


@login_required(login_url="login_or_signup_view")
def dashboard(request, profileId):
    if request.method=="POST":
        messageId=request.POST.get("message_id")
        print(messageId)
        if messageId:
            message=TrendingMessage.objects.filter(pk=messageId)
            message.delete()
    
    user = User.objects.get(username=profileId)
    trendingmessages = TrendingMessage.objects.filter(
        user=user, parent_message=None
    ).order_by("-date_added")
    popular_users = User.objects.annotate(follow_count=Count('following')).order_by('-follow_count')[:3]
    trendingmessagescount = len(trendingmessages)
    followers = user.profile.follow.all()
    following = user.profile.following.all()

    follow_count = user.profile.follow_count
    following_count = user.profile.following_count
    bio = user.profile.bio

    posts = TrendingMessage.objects.filter(user=user)
    total_viewcount = TrendingMessage.objects.filter(user=user).aggregate(
        Sum("view_count")
    )["view_count__sum"]
    return render(
        request,
        "main/dashboard.html",
        {
            "user": user,
            "trendingmessagescount": trendingmessagescount,
            "trendingmessages": trendingmessages,
            "follow_count": follow_count,
            "following_count": following_count,
            "bio": bio,
            "posts": posts,
            "followingUsers": following,
            "followUsers": followers,
            "total_viewcount": total_viewcount,
            "popular_users":popular_users,
        },
    )


@login_required(login_url="login_or_signup_view")
def view_message(request, message_id):
    

    message = get_object_or_404(TrendingMessage, id=message_id)
    hashtags = Hashtag.objects.all()[:3]
    replies = message.replies.all().order_by("-likes")
    return render(
        request, "main/view_message.html", {"message": message, "replies": replies,"hashtags":hashtags}
    )


@login_required(login_url="login_or_signup_view")
def messenger(request):
    user = request.user
    followingUsers = user.profile.following.all()
    conversations = Conversation.objects.filter(members__in=[user])

    return render(
        request,
        "main/messenger.html",
        {"followingUsers": followingUsers, "conversations": conversations},
    )


@login_required(login_url="login_or_signup_view")
def conversation(request, conversation_id):
    conversation = Conversation.objects.filter(members=request.user).get(
        pk=conversation_id
    )

    conversation_message = ConversationMessage.objects.filter(conversation=conversation)

    return render(
        request,
        "conversation/conversation.html",
        {"conversation": conversation, "conversation_messages": conversation_message},
    )

def notfication(request,username):
    notifications=Notification.objects.filter(user=request.user,seen=False)
    popular_users = User.objects.annotate(follow_count=Count('following')).order_by('-follow_count')[:3]
    hashtags = Hashtag.objects.all()[:3]
    return render(request,"main/notifications.html",{'notifications':notifications,'popular_users':popular_users,'hashtags':hashtags})


from django.contrib.auth import update_session_auth_hash


@login_required(login_url="login_or_signup_view")
def settings(request):
    images1 = [
        "/media/images/boy.png",
        "/media/images/dog.png",
        "/media/images/dinosaur.png",
        "/media/images/panda.png",
    ]

    images2= [
        "/media/images/hacker.png",
        "/media/images/chicken.png",
        "/media/images/bear.png",
        "/media/images/cat.png",
    ]

    if request.method=='POST':
        unblock_username=request.POST.get("unblock")
        if unblock_username:
            unblock_user=User.objects.get(username=unblock_username)
            request.user.profile.blocked_user.remove(unblock_user)
            return render(
                    request,
                    "main/setting.html",{"error_message":"User unblocked","status":"success","images1":images1,"images2":images2},
                    )
        delete_acc=request.POST.get("delete-acc")
        image_url=request.POST.get("image_path")
        loggedusername=request.POST.get("username")
        current_pass=request.POST.get("current-password")
        new_password=request.POST.get("new-password")
        confirm_password=request.POST.get("confirm-password")
        print(delete_acc)
        if delete_acc and current_pass:
            try:
                user=User.objects.get(username=request.user.username)
                if authenticate(username=request.user.username,password=current_pass):
                    user=User.objects.get(username=request.user.username)
                    user.delete()
                    return redirect("login_or_signup_view")
                else:
                    error_message="Invalid username or password"
                    return render(
                    request,
                    "main/setting.html",{"error_message":error_message,"images1":images1,"images2":images2},
                    )
            except:
                error_message="Invalid username or password"
                return render(
                request,
                "main/setting.html",{"error_message":error_message,"images1":images1,"images2":images2},
                )
        elif delete_acc and not current_pass:
            error_message="Plzz enter the password"
            return render(
                request,
                "main/setting.html",{"error_message":error_message,"images1":images1,"images2":images2},
                )

        elif loggedusername==request.user.username and current_pass and new_password and confirm_password:
            try:
                user=User.objects.get(username=request.user.username)
                if user and authenticate(username=loggedusername,password=current_pass):
                    if confirm_password==new_password:
                        image_url_without=image_url.replace("/media","")
                        user.profile.profile_img=image_url_without
                        user.profile.save()
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)
                        return redirect(dashboard,profileId=loggedusername)
                    else:
                        error_message="Passwords do not match!"
                else:
                    error_message="Plzz check your password"
            except:
                error_message="Invalid username or password"
                print(error_message)

        else:
            error_message="Check the data you have entered"
        return render(
        request,
        "main/setting.html",{"error_message":error_message,"images1":images1,"images2":images2},
    )



    return render(
        request,
        "main/setting.html",{"images1":images1,"images2":images2},
    )


def inviteview(request):
    current_url = reverse('index')
    # Now 'current_url' contains the absolute URL of the current page
    # ...

    return render(request, 'main/invite.html', {'current_url': current_url})