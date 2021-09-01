"""
ASGI config for RealTimeStockNotify project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RealTimeStockNotify.settings')

from Stocks.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack

# needed if starting server using the daphne or uvicorn command
import django
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
    # Just HTTP for now. (We can add other protocols later.)
})
