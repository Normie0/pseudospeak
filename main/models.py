from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class Profile(models.Model):
    user=models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    profile_img=models.ImageField(null=True,blank=True,upload_to='images/')

    def __str__(self) -> str:
        return str(self.user)
    
class TrendingMessage(models.Model):
    user=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    content=models.TextField()
    date_added = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        ordering = ('-date_added',)

    def __str__(self) :
        return f'{self.user}->{self.content}'