import jwt
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()

@database_sync_to_async
def get_user(validated_token):
    try:
        user_id = validated_token[api_settings.USER_ID_CLAIM]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get("token", [])
        print(token_list)

        if token_list:
            token = token_list[0]
            try:
                validated_token = UntypedToken(token)
                scope["user"] = await get_user(validated_token)
            except (InvalidToken, jwt.ExpiredSignatureError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
