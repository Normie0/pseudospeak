from django.urls import path
from . import consumers

websocket_urlpatterns=[
    path('ws/room/',consumers.RoomConsumer.as_asgi()),
    path('ws/messenger/<str:room_name>/',consumers.ChatConsumer.as_asgi()),
]