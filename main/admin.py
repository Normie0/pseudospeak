from django.contrib import admin
from .models import Profile,TrendingMessage,Hashtag,ReportUser

admin.site.register(Profile)
admin.site.register(TrendingMessage)
admin.site.register(Hashtag)
admin.site.register(ReportUser)