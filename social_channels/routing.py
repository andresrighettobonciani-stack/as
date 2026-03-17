from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.GlobalChatConsumer.as_asgi()),
    re_path(r'ws/channels/$', consumers.ChannelConsumer.as_asgi()),
    re_path(r'ws/channels/(?P<channel_slug>\w+)/$', consumers.ChannelDetailConsumer.as_asgi()),
]
