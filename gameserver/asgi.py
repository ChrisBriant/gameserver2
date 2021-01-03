# mysite/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
#import chat.routing
import risla.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

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
