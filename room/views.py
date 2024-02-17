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
            if len(rooms)<3:
                rooms = Room.objects.exclude(users=request.user).annotate(user_count=models.Count('users')).order_by('-user_count')[:5]
        else:
            rooms = Room.objects.exclude(users=request.user).annotate(user_count=models.Count('users')).order_by('-user_count')[:5]
    else:
        category=Category.objects.get(name=name)
        rooms = Room.objects.filter(~Q(users=user) & Q(category=category))
        print(name)

    return render(request,"room/rooms.html",{'rooms':rooms,'joinedRooms':joinedRooms,'categories':categories})



def room(request, slug):
    if request.method=='POST':
        user=request.user
        room=Room.objects.get(slug=slug)
        room.users.remove(user)
        room.save()
        return redirect(rooms,name="recommended")
    room=Room.objects.get(slug=slug)
    messages=Message.objects.filter(room=room)
    for message in messages:
        print(message.decrypt_message())
    return render(request, 'room/room.html', {'room': room, 'messages': messages})
