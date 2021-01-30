from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf.urls import url
import interviews.routing


from urllib.parse import unquote, parse_qs
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(params):
    try:
        if ("token" in params and len(params["token"]) >= 1):
            token = Token.objects.get(key=params["token"][0])
            return token.user
        else:
            return AnonymousUser()
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        unquoted_url = unquote(scope["query_string"].decode())
        params = parse_qs(unquoted_url)
        scope['user'] = await get_user(params)
        return await self.inner(scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(interviews.routing.websocket_urlpatterns)
    ),
})