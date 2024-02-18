from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from faker import Faker
from .forms import *
import random
from .models import Profile, TrendingMessage, Hashtag
from django.db.models import Sum, OuterRef
from conversation.models import Conversation, ConversationMessage


def generate_unique_username():
    fake = Faker()

    while True:
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            return username


def get_random_image():
    images = [
        "images/girl.jpg",
        "images/ninja.jpg",
        "images/fire.jpg",
        "images/panda.jpg",
    ]
    return random.choice(images)


@login_required(login_url="login_or_signup_view")
# Create your views here.
def index(request):
    messages = TrendingMessage.objects.filter(parent_message=None).order_by(
        "-custom_ordering"
    )
    hashtags = Hashtag.objects.all()[:3]
    return render(
        request, "main/index.html", {"messages": messages, "hashtags": hashtags}
    )


def hashtagMessages(request, hashtag):
    tag = f"#{hashtag}"
    try:
        hashtag = Hashtag.objects.get(tag=tag)
    except Hashtag.DoesNotExist:
        hashtag = None
    messages = TrendingMessage.objects.filter(parent_message=None, hashtags=hashtag)
    hashtags = Hashtag.objects.all()[:3]
    return render(
        request,
        "main/hashtagMessages.html",
        {"hashtag": hashtag, "messages": messages, "hashtags": hashtags},
    )


def login_or_signup_view(request):
    username = generate_unique_username()
    if request.method == "POST":
        action = request.POST.get("action")
        print(action)

        if action == "signup":
            print("This method is working")
            username = request.POST.get("username")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            try:
                existing_user = User.objects.get(username=username)
            except User.DoesNotExist:
                existing_user = None
            if confirm_password == password and existing_user is None:
                # Create the user first
                create_user = User.objects.create_user(
                    username=username, password=password
                )
                random_image_path = get_random_image()

                # Create the user's profile with the random image
                profile = Profile(
                    user=create_user, profile_img=random_image_path, bio="New User"
                )
                print("completed registering user")
                profile.save()
                login(request, create_user)
                return redirect("index")

            else:
                if confirm_password != password:
                    error_message=f'Passwords do not match'
                else:
                    error_message=f'User with username - {existing_user.username} already exists!'
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
    user = User.objects.get(username=profileId)
    trendingmessages = TrendingMessage.objects.filter(
        user=user, parent_message=None
    ).order_by("-date_added")

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
    print(total_viewcount)
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
        },
    )

@login_required(login_url="login_or_signup_view")
def view_message(request, message_id):
    if request.method == "POST":
        content = request.POST.get("replied_content")
        print(content)
        parent_message = get_object_or_404(TrendingMessage, id=message_id)
        user = request.user
        if user:
            replied_message = TrendingMessage(
                user=user, content=content, parent_message=parent_message
            )
            replied_message.save()
            return redirect(reverse("view_message", args=[message_id]))

    message = get_object_or_404(TrendingMessage, id=message_id)
    replies = message.replies.all().order_by("date_added")
    return render(
        request, "main/view_message.html", {"message": message, "replies": replies}
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
