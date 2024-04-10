from django.contrib import admin
from .models import Profile,TrendingMessage,Hashtag,ReportUser,Notification

admin.site.register(Profile)
admin.site.register(TrendingMessage)
admin.site.register(Hashtag)
admin.site.register(ReportUser)
admin.site.register(Notification)