from django.urls import path
from . import consumers

websocket_urlpatterns=[
    path("ws/",consumers.IndexConsumer.as_asgi()),
    path("ws/notification/messages/<str:username>/",consumers.NotificationConsumer.as_asgi()),
    path("ws/dashboard/<str:username>/",consumers.DashboardConsumer.as_asgi()),
    path("ws/messenger/",consumers.MessengerConsumer.as_asgi()),
    path("ws/message/<int:messageId>/",consumers.ReplyConsumer.as_asgi()),
    path("ws/messenger/conversation/<int:id>/",consumers.ConversationConsumer.as_asgi()),
]