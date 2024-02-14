import base64
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings

f=Fernet(settings.ENCRYPT_KEY)

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class Room(models.Model):
    users=models.ManyToManyField(User,related_name='joined_user')
    name=models.CharField(max_length=255)
    slug=models.SlugField(unique=True)
    room_img=models.ImageField(null=True)
    category=models.ForeignKey(Category,null=True,on_delete=models.CASCADE)

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

    def decrypt_message(self):  # Replace with your actual secret key
        try:
            print("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
            message_decrypted=f.decrypt(self.content)
            message_decoded=message_decrypted.decode('utf-8')
            return message_decoded
        except Exception as e:
            print(f"InvalidToken exception: {e.__cause__}")
            return "Invalid decryption token"


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
    
