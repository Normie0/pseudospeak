from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Conversation(models.Model):
    members = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-modified_at',)
    
    def __str__(self):
        l1=[]
        for m in self.members.all():
            l1.append(m.username)
        return str(l1)
    
class ConversationMessage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_messages', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) :
        return f'[{self.conversation}-{self.created_by}->{self.content}'