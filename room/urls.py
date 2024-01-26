from django.urls import path
from . import views

urlpatterns=[
    path("<str:name>/",views.rooms,name="rooms"),
    path("categories/<slug:slug>",views.room,name="room")
]