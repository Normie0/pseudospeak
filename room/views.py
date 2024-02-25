from django.shortcuts import render,redirect
from .models import *
from main.models import Profile
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from cryptography.fernet import Fernet
# Create your views here.
@login_required
def rooms(request,name):
    user=request.user
    joinedRooms=Room.objects.filter(users=user)
    categories=Category.objects.all()
    if name=='recommended':
        followingUsers=user.profile.following.all()
        print(len(followingUsers))
        if followingUsers:
            rooms = Room.objects.exclude(users=user).filter(Q(users__in=followingUsers) | Q(users=None)).annotate(user_count=models.Count('users')).order_by('-user_count')
            if len(rooms)<5:
                rooms = Room.objects.exclude(users=request.user).annotate(user_count=models.Count('users')).order_by('-user_count')[:5]
        else:
            rooms = Room.objects.exclude(users=request.user).annotate(user_count=models.Count('users')).order_by('-user_count')[:5]
    else:
        category=Category.objects.get(name=name)
        print(category.name)
        rooms = Room.objects.filter(~Q(users=user) & Q(category=category))
        print(name)

    return render(request,"room/rooms.html",{'rooms':rooms,'joinedRooms':joinedRooms,'categories':categories})



def room(request, slug):
    if request.method=='POST':
        user=request.user
        action=request.POST.get("delorexit")
        btnvalue=request.POST.get("confirmation")
        if action=="delete" and btnvalue=="yes":
            room=Room.objects.get(slug=slug)
            room.delete()
            return redirect(rooms,name="recommended")
        elif action is None:
            # print(btnvalue)
            if btnvalue=="yes":
                room.users.remove(user)
                room.save()
                return redirect(rooms,name="recommended")
    room=Room.objects.get(slug=slug)
    messages=Message.objects.filter(room=room)
    return render(request, 'room/room.html', {'room': room, 'messages': messages})

def create_room(request):
    if request.method=="POST":
        try:
            name=request.POST.get("group-name")
            category_name=request.POST.get("cars")
            file=request.FILES.get("group-avatar")
            error_message=None
            print(name)
            print(category_name)
            if file is None:
                error_message=f"Group image is required to create group"
            elif file.size > 1024 * 1024:
                error_message="File size should be less than 2MB"
            slug_with_space=name.lower()
            slug=slug_with_space.replace(" ","")
            try:
                existing_group=Room.objects.get(slug=slug)
            except:
                existing_group=None
            print(slug)
            if name and category_name and file and existing_group is None and error_message is None:
                category=Category.objects.get(name=category_name)
                createroom=Room.objects.create(name=name,owner=request.user,slug=slug,room_img=file,category=category)
                createroom.users.add(request.user)
                if createroom.save():
                    print("Success")
                return redirect(room,slug)
            else:
                if existing_group is not None:
                    error_message=f"Group with group name '{existing_group.name}' already exists"
                return render(request,"room/create-group.html",{'error_message':error_message})
        except ValueError as e:
            error_message=e
            return render(request,"room/create-group.html",{'error_message':error_message})
    return render(request,'room/create-group.html')

