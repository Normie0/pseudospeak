from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def rooms(request):
    user=request.user
    rooms=Room.objects.exclude(users=user)
    joinedRooms=Room.objects.filter(users=user)
    return render(request,"room/rooms.html",{'rooms':rooms,'joinedRooms':joinedRooms})


@login_required
def room(request,slug):
    room=Room.objects.get(slug=slug)
    messages=Message.objects.filter(room=room)
    return render(request,'room/room.html',{'room':room,'messages':messages})