from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path("",views.index,name="index"),
    path('view_message/<int:message_id>/', views.view_message, name='view_message'),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("signup/",views.login_or_signup_view,name="login_or_signup_view"),
    path("logout/",views.logoutuser,name="logout"),
    path('invite/', views.invite_view, name='invite'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)