# mysite/asgi.py
#Read below for daphne configuration
#https://www.gitmemory.com/issue/django/channels/1564/722354397

import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gameserver.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
#import chat.routing
import risla.routing



application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            risla.routing.websocket_urlpatterns
        )
    ),
})

# application = ProtocolTypeRouter({
#   "http": get_asgi_application(),
#   "websocket": SessionMiddlewareStack(
#         URLRouter(
#             risla.routing.websocket_urlpatterns
#         )
#     ),
# })
