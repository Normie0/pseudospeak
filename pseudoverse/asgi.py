import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import room.routing
import main.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochat.settings')

# Combine the WebSocket URL patterns from room and main apps into a single list
websocket_urlpatterns = []
websocket_urlpatterns.extend(room.routing.websocket_urlpatterns)
websocket_urlpatterns.extend(main.routing.websocket_urlpatterns)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})
