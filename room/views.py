from django.shortcuts import render,redirect
from .models import *
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
        rooms = Room.objects.exclude(users=request.user).annotate(user_count=models.Count('users')).order_by('-user_count')[:3]
        print("Done")
    else:
        category=Category.objects.get(name=name)
        rooms = Room.objects.filter(~Q(users=user) & Q(category=category))
        print(name)

    return render(request,"room/rooms.html",{'rooms':rooms,'joinedRooms':joinedRooms,'categories':categories})



def room(request, slug):
    room=Room.objects.get(slug=slug)
    messages=Message.objects.filter(room=room)
    for message in messages:
        print(message.decrypt_message())
    return render(request, 'room/room.html', {'room': room, 'messages': messages})
