from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet

f=Fernet(settings.ENCRYPT_KEY)

class Profile(models.Model):
    user=models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    blocked_user=models.ManyToManyField(User,related_name="block_users",blank=True)
    profile_img=models.ImageField(null=True,blank=True,upload_to='images/')
    bio=models.CharField(null=True,max_length=51)
    follow=models.ManyToManyField(User,related_name='follow',blank=True)
    following=models.ManyToManyField(User,related_name='following',blank=True)
    
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
    userLiked=models.ManyToManyField(User,related_name='user_like',blank=True)
    view_count=models.IntegerField(null=True,default=0)
    viewed=models.ManyToManyField(User,related_name='viewed',blank=True)
    hashtags=models.ManyToManyField('Hashtag',blank=True)
    date_added = models.DateTimeField(auto_now_add=True,null=True)
    parent_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    custom_ordering = models.FloatField(default=0)

    #poll
    option1 = models.CharField(max_length=100, blank=True,null=True)
    option2 = models.CharField(max_length=100, blank=True,null=True)
    voted = models.ManyToManyField(User, related_name='voted', blank=True, null=True)

    # Votes for poll options
    votes_option1 = models.IntegerField(default=0,blank=True,null=True)
    votes_option2 = models.IntegerField(default=0,blank=True,null=True)

    def decrypt_message(self):  # Replace with your actual secret key
        try:
            message_decrypted=f.decrypt(self.content)
            message_decoded=message_decrypted.decode('utf-8')
            return message_decoded
        except Exception as e:
            print(f"InvalidToken exception: {e.__cause__}")
            return "Invalid decryption token"
        
    def option1_count(self):
        total=self.votes_option1+self.votes_option2
        if total==0:
            return 0;
        option1_percent=(self.votes_option1/total)*100
        return int(option1_percent)
    
    def option2_count(self):
        total=self.votes_option1+self.votes_option2
        if total==0:
            return 0;
        option2_percent=(self.votes_option2/total)*100
        return int(option2_percent)


    def save(self, *args, **kwargs):
        # Your custom logic to calculate the ordering value
        self.custom_ordering = (0.7 * self.view_count) + (0.3 * self.likes)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['custom_ordering']

    def __str__(self) :
        return f'{self.user}->{self.content}'
    
class Hashtag(models.Model):
    tag=models.CharField(max_length=255)
    count=models.IntegerField(default=1,null=True)

    class Meta:
        ordering = ('-count',)


    def __str__(self):
        return self.tag
    
class ReportUser(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    reason=models.CharField(max_length=20)
    additionalInfo=models.CharField(max_length=512,null=True,blank=True)

    def __str__(self) -> str:
        return f'Reported user={self.user.username} , reason={self.reason} , info-{self.additionalInfo}'
