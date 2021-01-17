# mysite/asgi.py
import os, django

from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
#import chat.routing
import risla.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

application = get_default_application()

