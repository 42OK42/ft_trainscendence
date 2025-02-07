from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models.game import PongGame
from .models.player import Player, PlayerType, Controls
import uuid
import asyncio

class MatchmakingConsumer(AsyncWebsocketConsumer):
    waiting_players = {}  # {websocket: user}
    active_games = {}     # {game_id: {player1: websocket, player2: websocket}}

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()

    async def disconnect(self, close_code):
        if self in self.waiting_players:
            del self.waiting_players[self]
            for ws in self.waiting_players:
                await ws.send(json.dumps({
                    'action': 'search_cancelled',
                    'message': 'Ein Spieler hat die Suche abgebrochen.'
                }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'find_game':
            await self.find_game()
        elif action == 'cancel_search':
            await self.cancel_search()

    async def find_game(self):
        if self.waiting_players:
            other_socket, other_user = next(iter(self.waiting_players.items()))
            del self.waiting_players[other_socket]
            
            game_id = str(uuid.uuid4())
            
            # Benachrichtige beide Spieler
            await other_socket.send(json.dumps({
                'action': 'game_found',
                'opponent': self.user.username,
                'game_id': game_id
            }))
            
            await self.send(json.dumps({
                'action': 'game_found',
                'opponent': other_user.username,
                'game_id': game_id
            }))

            # Starte das Spiel nach kurzer Verzögerung
            await asyncio.sleep(2)
            await self.start_game(game_id)
        else:
            self.waiting_players[self] = self.user
            await self.send(json.dumps({
                'action': 'searching_game'
            }))

    async def start_game(self, game_id):
        # Nur das Signal zum Spielstart senden
        await self.send(json.dumps({
            'action': 'start_game',
            'game_id': game_id
        }))

    async def cancel_search(self):
        if self in self.waiting_players:
            del self.waiting_players[self]
            for ws in self.waiting_players:
                await ws.send(json.dumps({
                    'action': 'search_cancelled',
                    'message': 'Ein Spieler hat die Suche abgebrochen.'
                }))
        await self.send(json.dumps({
            'action': 'search_cancelled',
            'message': 'Suche abgebrochen.'
        }))

    async def handle_game_disconnect(self, game_id):
        if game_id in self.active_games:
            game = self.active_games[game_id]
            # Notify other player about disconnect
            for socket in game.values():
                if socket != self:
                    await socket.send(json.dumps({
                        'action': 'opponent_disconnected'
                    }))
            # Cleanup
            del self.active_games[game_id] 