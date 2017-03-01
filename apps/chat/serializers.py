from django.contrib.auth.models import AbstractUser, User
from rest_framework import serializers

from apps.chat.models import Message


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150,
                                     validators=[AbstractUser.username_validator])
    password = serializers.CharField(max_length=128)


class RegisterUserSerializer(UserSerializer):
    repeat_password = serializers.CharField(max_length=128)


class MessageSerializer(serializers.Serializer):
    from_user = serializers.CharField(max_length=150,
                                      validators=[AbstractUser.username_validator])
    to_user = serializers.CharField(max_length=150,
                                    validators=[AbstractUser.username_validator],
                                    allow_null=True)
    timestamp = serializers.IntegerField()
    text = serializers.CharField()
    
    def create(self, validated_data):
        to_user = None
        if validated_data['to_user'] is not None:
            to_user = User.objects.get(username=validated_data['to_user'])
        
        message = Message.objects.create(from_user=User.objects.get(username=validated_data['from_user']),
                                         to_user=to_user,
                                         timestamp=validated_data['timestamp'],
                                         text=validated_data['text'])
        return message