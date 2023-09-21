from django.contrib import admin
from .models import Profile,TrendingMessage,Hashtag

admin.site.register(Profile)
admin.site.register(TrendingMessage)
admin.site.register(Hashtag)