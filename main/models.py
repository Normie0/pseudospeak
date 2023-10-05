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
    image=models.ImageField(null=True,blank=True)
    likes=models.IntegerField(null=True,default=0)
    view_count=models.IntegerField(null=True,default=0)
    hashtags=models.ManyToManyField('Hashtag')
    date_added = models.DateTimeField(auto_now_add=True,null=True)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ('-date_added',)

    def __str__(self) :
        return f'{self.user}->{self.content}'
    
class Hashtag(models.Model):
    tag=models.CharField(max_length=255)
    count=models.IntegerField(default=1,null=True)

    class Meta:
        ordering = ('-count',)


    def __str__(self):
        return self.tag