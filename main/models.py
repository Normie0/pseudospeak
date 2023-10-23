from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class Profile(models.Model):
    user=models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    profile_img=models.ImageField(null=True,blank=True,upload_to='images/')
    bio=models.CharField(null=True,max_length=512)
    follow=models.ManyToManyField(User,related_name='follow')
    following=models.ManyToManyField(User,related_name='following')

    def __str__(self) -> str:
        return str(self.user)
    
    @property
    def follow_count(self):
        return self.follow.count()
    
    @property
    def following_count(self):
        return self.following.count()
    
class TrendingMessage(models.Model):
    user=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    content=models.TextField()
    image=models.ImageField(null=True,blank=True,upload_to="images/")
    likes=models.IntegerField(null=True,default=0)
    userLiked=models.ManyToManyField(User,related_name='user_like')
    view_count=models.IntegerField(null=True,default=0)
    viewed=models.ManyToManyField(User,related_name='viewed')
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