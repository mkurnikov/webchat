from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Message(models.Model):
    from_user = models.ForeignKey(User, related_name='messages_sent')
    to_user = models.ForeignKey(User, null=True, related_name='messages_received')
    
    text = models.TextField()
    timestamp = models.IntegerField()
    
    
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)