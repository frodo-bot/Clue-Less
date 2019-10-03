# clueless_project/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import clueless.routing

application = ProtocolTypeRouter({
     # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            clueless.routing.websocket_urlpatterns
        )
    ),
})