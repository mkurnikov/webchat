from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from apps.chat.models import Message
from apps.chat.tests.base import AuthenticatedClientFactory


class TestRegistration(TestCase):
    def test_create_user(self):
        username = 'asdf'
        password = 'password'
        response = self.client.post(reverse('register'), data={
            'username': username,
            'password': password,
            'repeat_password': password
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get_by_natural_key(username)  # type: User
        self.assertTrue(user.check_password(password))
    
    def test_fail_if_user_exists(self):
        username = 'asdf'
        password = 'password'
        user = User.objects.create_user(username, password=password)
        
        response = self.client.post(reverse('register'), data={
            'username': username,
            'password': password,
            'repeat_password': password
        })
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)


class TestLogin(TestCase):
    def setUp(self):
        self.username = 'asdf'
        self.password = 'password'
        User.objects.create_user(self.username, password=self.password)
    
    def test_successful_login(self):
        response = self.client.post(reverse('login'), data={
            'username': self.username,
            'password': self.password
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'],
                         User.objects.get_by_natural_key(self.username).auth_token.key)
        
    def test_fails_if_not_exists(self):
        response = self.client.post(reverse('login'), data={
            'username': 'unknown_username',
            'password': self.password
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_fails_if_wrong_password(self):
        response = self.client.post(reverse('login'), data={
            'username': self.username,
            'password': '123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPublicChat(TestCase):
    def setUp(self):
        username = 'asdf'
        self.user = User.objects.create_user(username, password='password')
        
        self.auth_client = AuthenticatedClientFactory().client(username)
    
    def test_cannot_send_messages_without_token(self):
        response = self.client.post(reverse('public-chat'), data={
            'text': 'anytext'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_post_public_message(self):
        response = self.auth_client.post(reverse('public-chat'), data={
            'text': 'anytext'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        message = Message.objects.all()[0]
        self.assertEqual(message.text, 'anytext')
    
    def test_get_all_public_messages_ordered(self):
        Message.objects.create(from_user=self.user, to_user=None, timestamp=13, text='anytext1')
        Message.objects.create(from_user=self.user, to_user=None, timestamp=11, text='anytext2')
        
        response = self.auth_client.get(reverse('public-chat'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        message_json1 = response.data[0]
        self.assertEqual(message_json1['from_user'], self.user.username)
        self.assertEqual(message_json1['timestamp'], 11)
        
        message_json2 = response.data[1]
        self.assertEqual(message_json2['timestamp'], 13)


class TestPrivateChat(TestCase):
    def setUp(self):
        self.username1 = 'asdf1'
        self.username2 = 'asdf2'
        self.user1 = User.objects.create_user(self.username1, password='password')
        self.user2 = User.objects.create_user(self.username2, password='password')
        
        self.auth_client1 = AuthenticatedClientFactory().client(self.username1)
        self.auth_client2 = AuthenticatedClientFactory().client(self.username2)
    
    def test_list_users(self):
        response = self.auth_client1.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual({self.username1, self.username2}, set(response.data))
    
    def test_exchange_messages_with_user(self):
        in_message1 = 'Hello, {username}'.format(username=self.username2)
        response = self.auth_client1.post(reverse('private-chat'), {
            'to_user': self.username2,
            'text': 'Hello, {username}'.format(username=self.username2)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        in_message2 = 'Hello too, {username}'.format(username=self.username1)
        response = self.auth_client2.post(reverse('private-chat'), {
            'to_user': self.username1,
            'text': 'Hello too, {username}'.format(username=self.username1)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.auth_client1.get(reverse('private-chat'), data={
            'history_with': self.username2
        })
        message1 = response.data[0]
        message2 = response.data[1]
        
        self.assertEqual(message1['text'], in_message1)
        self.assertEqual(message2['text'], in_message2)
