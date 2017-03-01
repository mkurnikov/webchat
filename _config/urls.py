from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from apps.chat.views import PublicChatView, RegistrationView, LoginView, UserListView, PrivateChatView


urlpatterns = [
    url('^public-chat/$', PublicChatView.as_view(), name='public-chat'),
    url('^register/', RegistrationView.as_view(), name='register'),
    url('^login/', LoginView.as_view(), name='login'),
    url('^users/', UserListView.as_view(), name='user-list'),
    url('^private/', PrivateChatView.as_view(), name='private-chat')
]

urlpatterns += [
    # url(r'^api-auth/', include('rest_framework.urls',
    #                            namespace='rest_framework')),
    url('^{swagger_root}/'.format(swagger_root=settings.SWAGGER_ROOT_FOLDER.strip('/')),
        include('rest_framework_swagger.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
