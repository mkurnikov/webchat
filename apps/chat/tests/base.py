from django.contrib.auth.models import User
from rest_framework.test import APIClient


class AuthenticatedClientFactory():
    def client(self, username: str) -> APIClient:
        user = User.objects.get_by_natural_key(username)
        token_key = user.auth_token.key
        return TokenizedAPIClient(token_key)


class TokenizedAPIClient(APIClient):
    def __init__(self, auth_token: str, enforce_csrf_checks=False, **defaults):
        super().__init__(enforce_csrf_checks=enforce_csrf_checks, **defaults)
        self.auth_token = 'Token {token}'.format(token=auth_token)
    
    def _add_auth_header(self, extra):
        extra['HTTP_AUTHORIZATION'] = self.auth_token
    
    def get(self, path, data=None, follow=False, **extra):
        self._add_auth_header(extra)
        return super().get(path, data=data, follow=follow, **extra)
    
    def post(self, path, data=None, format='json', content_type=None,
             follow=False, **extra):
        self._add_auth_header(extra)
        return super().post(path, data=data, format=format, content_type=content_type, follow=follow,
                            **extra)
    
    def put(self, path, data=None, format='json', content_type=None,
            follow=False, **extra):
        self._add_auth_header(extra)
        return super().put(path, data=data, format=format, content_type=content_type, follow=follow,
                           **extra)
    
    def patch(self, path, data=None, format='json', content_type=None,
              follow=False, **extra):
        self._add_auth_header(extra)
        return super().patch(path, data=data, format=format, content_type=content_type, follow=follow,
                             **extra)
    
    def delete(self, path, data=None, format='json', content_type=None,
               follow=False, **extra):
        self._add_auth_header(extra)
        return super().delete(path, data=data, format=format, content_type=content_type, follow=follow,
                              **extra)