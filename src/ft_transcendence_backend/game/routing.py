from django.urls import re_path
from . import matchmaking

websocket_urlpatterns = [
    re_path(r'ws/game/matchmaking$', matchmaking.MatchmakingConsumer.as_asgi()),
] 
