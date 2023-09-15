from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from faker import Faker
from .forms import *
import random
from .models import Profile,TrendingMessage


def generate_unique_username():
    fake = Faker()
    
    while True:
        username = fake.user_name()
        if not User.objects.filter(username=username).exists():
            return username
        
def get_random_image():
    images=['images/teddy.jpg','images/toycar.jpg','images/Woody.jpg']
    return random.choice(images)


# Create your views here.
def index(request):
    if request.method=='POST':
        name=request.POST.get('editUser')
        user=request.user
        user.username=name
        user.save()
        return redirect('index')
    messages=TrendingMessage.objects.all()
    return render(request,"main/index.html",{'messages':messages})

def login_or_signup_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        print(action)
        
        if action == 'signup':
            print("This method is working")
            email = request.POST.get('email')
            password = request.POST.get('password1')
            # confirm_password = request.POST.get('confirm_password')
            confirm_password=password
            existing_email=get_object_or_404(User,email=email)
            username = generate_unique_username()  # Replace with your username generation logic
            print("completed fetching data from form")
            if confirm_password == password and existing_email is None:
                # Create the user first
                create_user = User.objects.create_user(username=username, email=email, password=password)
                random_image_path = get_random_image()
                
                # Create the user's profile with the random image
                profile = Profile(user=create_user, profile_img=random_image_path)
                print("completed registering user")
                profile.save()
                login(request, create_user)
                return redirect('index')
                
            else:
                return render(request, 'main/signup.html', {'error_message': 'Passwords do not match'})

        elif action == 'login':
            email = request.POST.get('email')
            password = request.POST.get('password')
            print("This is a login action")
            current_user=get_object_or_404(User,email=email)
            print(current_user.username)
            user = authenticate(request, username=current_user.username, password=password)
            print(user)

            if user:
                login(request, user)
                return redirect('index')
            else:
                return render(request, 'main/signup.html', {'error_message': 'Invalid email or password'})

    return render(request, 'main/signup.html')

def logoutuser(request):
    logout(request)
    return redirect('login_or_signup_view')

def dashboard(request):
    user=request.user
    trendingmessages=TrendingMessage.objects.filter(user=user)
    trendingmessagescount=len(trendingmessages)
    return render(request,'main/dashboard.html',{'trendingmessagescount':trendingmessagescount,'trendingmessages':trendingmessages})