from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from faker import Faker
from .forms import *
import random
from .models import Profile, TrendingMessage, Hashtag


def generate_unique_username():
    fake = Faker()

    while True:
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            return username


def get_random_image():
    images = ["images/teddy.jpg", "images/toycar.jpg", "images/Woody.jpg"]
    return random.choice(images)

@login_required(login_url='login_or_signup_view')
# Create your views here.
def index(request):
    messages = TrendingMessage.objects.filter(parent_message=None).order_by('-view_count')
    hashtags = Hashtag.objects.all()[:3]
    return render(
        request, "main/index.html", {"messages": messages, "hashtags": hashtags}
    )

def hashtagMessages(request,hashtag):
    tag=f'#{hashtag}'
    try:
        hashtag=Hashtag.objects.get(tag=tag)
    except Hashtag.DoesNotExist:
        hashtag=None
    messages=TrendingMessage.objects.filter(parent_message=None,hashtags=hashtag)
    hashtags = Hashtag.objects.all()[:3]
    return render(request,"main/hashtagMessages.html",{'hashtag':hashtag,'messages':messages,'hashtags':hashtags})

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
            confirm_password = password
            try:
                existing_user = User.objects.get(username=username)
            except User.DoesNotExist:
                existing_user = None
            print(existing_user)
            print("completed fetching data from form")
            if confirm_password == password and existing_user is None:
                # Create the user first
                create_user = User.objects.create_user(
                    username=username, password=password
                )
                random_image_path = get_random_image()

                # Create the user's profile with the random image
                profile = Profile(user=create_user, profile_img=random_image_path)
                print("completed registering user")
                profile.save()
                login(request, create_user)
                return redirect("index")

            else:
                return render(
                    request,
                    "main/signup.html",
                    {"error_message": "Passwords do not match","username": username},
                )

        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            print("This is a login action")
            user = authenticate(
                request, username=username, password=password
            )
            print(user)

            if user:
                login(request, user)
                return redirect('index')
            else:
                return render(
                    request,
                    "main/signup.html",
                    {"error_message": "Invalid username or password","username": username},
                )
    return render(request, "main/signup.html", {"username": username})


def logoutuser(request):
    logout(request)
    return redirect("login_or_signup_view")


def dashboard(request,profileId):
    user = User.objects.get(username=profileId)
    trendingmessages = TrendingMessage.objects.filter(
        user=user, parent_message=None
    ).order_by("date_added")
    trendingmessagescount = len(trendingmessages)
    return render(
        request,
        "main/dashboard.html",
        {
            "user":user,
            "trendingmessagescount": trendingmessagescount,
            "trendingmessages": trendingmessages,
        },
    )


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
