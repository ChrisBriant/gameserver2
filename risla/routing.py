# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    #re_path(r'ws/risla/(?P<room_name>\w+)/$', consumers.RoomConsumer.as_asgi()),
    re_path(r'ws/risla/$', consumers.PlayerConsumer.as_asgi()),
]
