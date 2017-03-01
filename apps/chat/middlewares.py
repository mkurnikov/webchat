import logging
from typing import Tuple

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response


MAX_BODY_LENGTH = 3000  # log no more than 3k bytes of content

swagger_request_logger = logging.getLogger('middlewares.swagger.request')
swagger_response_logger = logging.getLogger('middlewares.swagger.response')

request_logger = logging.getLogger('middlewares.request')
response_logger = logging.getLogger('middlewares.response')


class ResponseLoggingMiddleware(MiddlewareMixin):
    """ Logs requests and responses in the nice way: log bodies of the request and response, and code together
    in one place."""
    
    def process_request(self, request: WSGIRequest) -> None:
        if request.body:
            request._saved_body = str(self._chunked_to_max(request.body))
    
    def process_response(self, request: WSGIRequest, response: Response) -> Response:
        if type(response) == Response:
            if 200 <= response.status_code <= 399:
                level = logging.INFO
            elif 400 <= response.status_code <= 499:
                level = logging.WARN
            else:
                level = logging.ERROR
            
            _request_logger = request_logger
            _response_logger = response_logger
            # filter swagger-related messages in the separate loggers
            if request.get_full_path().strip('/').startswith(settings.SWAGGER_ROOT_FOLDER):
                _request_logger = swagger_request_logger
            if response.data and 'swaggerVersion' in response.data:
                _response_logger = swagger_response_logger
                
            request_msg, response_msg = self._build_messages(request, response)
            _request_logger.log(level, request_msg)
            _response_logger.log(level, response_msg)
        
        return response
    
    def _build_messages(self, request: WSGIRequest, response: Response) -> Tuple[str, str]:
        request_msg_parts = [request.method, request.get_full_path()]
        if hasattr(request, '_saved_body'):
            request_msg_parts.append(request._saved_body)
        request_msg = 'Request: ' + ' '.join(request_msg_parts)
        
        response_msg_parts = [str(response.status_code)]
        if response.data:
            response_msg_parts.append(str(response.data))
        response_msg = 'Response: ' + ' '.join(response_msg_parts)
        
        return request_msg, response_msg
    
    def _chunked_to_max(self, msg):
        return msg[0:MAX_BODY_LENGTH]
