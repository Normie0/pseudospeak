from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path("",views.index,name="index"),
    path("view_hashtag/message/<str:hashtag>/",views.hashtagMessages,name="hashtagMessages"),
    path('message/<int:message_id>/', views.view_message, name='view_message'),
    path('dashboard/<str:profileId>/', views.dashboard, name='dashboard'),
    path("authenticate/signup/",views.login_or_signup_view,name="login_or_signup_view"),
    path("authenticate/logout/",views.logoutuser,name="logout"),
    path("messenger/",views.messenger,name='messenger')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)