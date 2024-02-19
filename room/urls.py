from django.urls import path
from . import views

urlpatterns=[
    path("<str:name>/",views.rooms,name="rooms"),
    path("new/create_group/",views.create_room,name="create_room"),
    path("categories/<slug:slug>",views.room,name="room")
]