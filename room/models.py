from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Room(models.Model):
    users=models.ManyToManyField(User,related_name='joined_user',null=True)
    name=models.CharField(max_length=255)
    slug=models.SlugField(unique=True)

    def __str__(self) :
        return self.name
    
class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    content=models.TextField()
    image=models.ImageField(null=True,blank=True,upload_to="images/")
    likes=models.IntegerField(null=True,default=0)
    view_count=models.IntegerField(null=True,default=0)
    hashtags=models.ManyToManyField('Hashtag')
    date_added = models.DateTimeField(auto_now_add=True,null=True)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ('date_added',)

    def __str__(self) :
        return f'Message from {self.user.username} in room {self.room.name} content - {self.content}'
    
class Hashtag(models.Model):
    tag=models.CharField(max_length=255)
    count=models.IntegerField(default=1,null=True)

    class Meta:
        ordering = ('-count',)


    def __str__(self):
        return self.tag