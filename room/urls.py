from django.urls import path
from . import views

urlpatterns=[
    path("categories/",views.rooms,name="rooms"),
    path("categories/<slug:slug>",views.room,name="room")
]