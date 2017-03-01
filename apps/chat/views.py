import time

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.models import Message
from apps.chat.serializers import MessageSerializer, RegisterUserSerializer, UserSerializer


def get_current_timestamp() -> int:
    return int(time.time() * 1000)


class RegistrationView(APIView):
    def post(self, request: Request) -> Response:
        """
        ---
        consumes:
            - application/json
            
        request_serializer: RegisterUserSerializer
        
        responseMessages:
            - code: 201
              message: User record is created.
            - code: 400
              message: Invalid credentials.
              
        """
        serialized = RegisterUserSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serialized.errors)
        
        username = serialized.data['username']
        password = serialized.data['password']
        repeat_password = serialized.data['repeat_password']
        
        if password != repeat_password:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'errors': 'Passwords don\'t match.'
            })
        
        User.objects.create_user(username=username, password=password)
        return Response(status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request: Request) -> Response:
        """
        ---
        consumes:
            - application/json
            
        request_serializer: UserSerializer
        
        responseMessages:
            - code: 200
              message: Login is successful. Token provided in the output.
            - code: 400
              message: Bad request form.
            - code: 401
              message: Invalid credentials.
        """
        serialized = UserSerializer(data=request.data)
        if not serialized.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serialized.errors)
        
        username = serialized.data['username']
        password = serialized.data['password']
        
        user = User.objects.get_by_natural_key(username)  # type: User
        if not user.check_password(password):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(status=status.HTTP_200_OK, data={
            'token': user.auth_token.key
        })


class PublicChatView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request: Request) -> Response:
        # TODO: add yaml docs
        messages = []
        for message in Message.objects.filter(to_user__isnull=True):
            serialized_message = MessageSerializer(instance=message)
            messages.append(serialized_message.data)
        
        return Response(status=status.HTTP_200_OK, data=messages)
    
    def post(self, request: Request) -> Response:
        """
        ---
        consumes:
            - application/json
            
        parameters:
            - name: body
              description: Text of message
              required: true
              type: string
              paramType: body
            
        responseMessages:
            - code: 200
              message: Message has been sent correctly.
            - code: 400
              message: Bad request form.
            - code: 401
              message: Invalid credential token.
        
        """
        message_data = dict(request.data)
        message_data['from_user'] = request.user.username
        message_data['to_user'] = None
        message_data['timestamp'] = get_current_timestamp()
        
        new_message_serialized = MessageSerializer(data=message_data)
        if not new_message_serialized.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=new_message_serialized.errors)
        
        new_message_serialized.save()
        return Response(status=status.HTTP_200_OK)


class UserListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request: Request) -> Response:
        username_list = User.objects.all().values_list('username', flat=True)
        return Response(status=status.HTTP_200_OK, data=username_list)


class PrivateChatView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request: Request) -> Response:
        """ Get message history with user. """
        username = request.query_params['history_with']
        second_user = User.objects.get(username=username)
        
        message_history_ascending = ((Message.objects.filter(from_user=request.user, to_user=second_user) |
                                      Message.objects.filter(from_user=second_user, to_user=request.user))
                                     .order_by('timestamp'))
        message_history_serialized = []
        for message in message_history_ascending:
            message_history_serialized.append(MessageSerializer(instance=message).data)
            
        return Response(status=status.HTTP_200_OK, data=message_history_serialized)
        
    def post(self, request: Request) -> Response:
        """ Send message to user. """
        data = dict(request.data)
        data['from_user'] = request.user.username
        data['timestamp'] = get_current_timestamp()
        
        serialized = MessageSerializer(data=data)
        if not serialized.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serialized.errors)
        
        serialized.save()
        
        return Response(status=status.HTTP_200_OK)
        
        
