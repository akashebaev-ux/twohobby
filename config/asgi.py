"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


from django.core.asgi import get_asgi_application  # noqa

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa
from chat.routing import websocket_urlpatterns  # noqa

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
