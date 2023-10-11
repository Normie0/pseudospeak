from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path("",views.index,name="index"),
    path("<str:hashtag>/",views.hashtagMessages,name="hashtagMessages"),
    path('view_message/<int:message_id>/', views.view_message, name='view_message'),
    path("dashboard/profile/",views.dashboard,name="dashboard"),
    path("authenticate/signup/",views.login_or_signup_view,name="login_or_signup_view"),
    path("authenticate/logout/",views.logoutuser,name="logout"),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)