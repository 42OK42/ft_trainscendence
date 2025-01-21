from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
from player import Player  # Fixed import statement
import random
import math
from ai_player import AI  # neue Import
from menu_state import MenuState
from game_objects import Ball, Paddle  # Neue Imports
from contextlib import asynccontextmanager

# Globale Variable für aktive Spiele
games = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
	yield
	# Cleanup beim Beenden
	for game_id in games:
		for connection in games[game_id]["connections"]:
			try:
				await connection.close()
			except:
				pass
	games.clear()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Globaler Menüzustand
menu_state = MenuState()

class GameState:
	def __init__(self, with_ai=False, difficulty=0):
		self.player1 = Player(is_left_player=True, is_ai=False)  # Immer Human
		self.player2 = Player(is_left_player=False, is_ai=with_ai)  # AI wenn aktiviert
		self.with_ai = with_ai
		self.ai = AI(difficulty) if with_ai else None
		self.ball_x = 400
		self.ball_y = 250
		self.ball_dx = -5
		self.ball_dy = 5
		self.ball_speed = 3
		self.ball_radius = 10
		self.score_player1 = 0
		self.score_player2 = 0
		self.game_over = False
		self.winner = None
		self.reset_ball()

	def reset_game(self):
		"""Reset the entire game state"""
		self.score_player1 = 0
		self.score_player2 = 0
		self.game_over = False
		self.winner = None
		self.reset_ball()
		self.player1.reset()
		self.player2.reset()

	def reset_ball(self):
		"""Resets ball to center with random direction"""
		self.ball_x = 400
		self.ball_y = 250
		# Random angle between -45 and 45 degrees, or 135-225 degrees
		angle = random.choice([
			random.uniform(-math.pi/4, math.pi/4),
			random.uniform(3*math.pi/4, 5*math.pi/4)
		])
		self.ball_dx = math.cos(angle) * self.ball_speed
		self.ball_dy = math.sin(angle) * self.ball_speed

	def check_winner(self):
		if self.player1.score >= 5:
			self.game_over = True
			self.winner = "Player 1"
		elif self.player2.score >= 5:
			self.game_over = True
			self.winner = "Player 2"

	def handle_input(self, player_id: int, input_data: dict):
		"""Verarbeitet Spielereingaben"""
		if self.game_over:
			return

		# Hole den richtigen Spieler
		player = self.player1 if player_id == 1 else self.player2

		# Ignoriere Eingaben für AI-Spieler
		if player.is_ai:
			return

		if input_data.get("move"):
			direction = input_data.get("direction", 0)
			player.move(direction)

	def update_ball(self):
		"""Updates ball position and handles collisions"""
		if self.game_over:
			return

		# Update AI if player2 is AI
		if self.with_ai:
			ball = Ball(self.ball_x, self.ball_y, self.ball_dx, self.ball_dy)
			paddle = Paddle(self.player2.x, self.player2.y, self.player2.height)
			new_y = self.ai.update(ball, paddle, 500)
			self.player2.y = new_y

		# Update ball position
		self.ball_x += self.ball_dx
		self.ball_y += self.ball_dy
		
		# Wall collisions (top and bottom)
		if self.ball_y <= 0 or self.ball_y >= 500:
			self.ball_dy *= -1
			
		# Paddle collisions
		for player in [self.player1, self.player2]:
			if (player.x <= self.ball_x <= player.x + player.width and
				player.y <= self.ball_y <= player.y + player.height):
				self.ball_dx *= -1
				break
				
		# Score points
		if self.ball_x <= 0:
			self.score_player2 += 1
			self.check_winner()
			self.reset_ball()
		elif self.ball_x >= 800:
			self.score_player1 += 1
			self.check_winner()
			self.reset_ball()

	def to_dict(self):
		"""Converts game state to dictionary for JSON transmission"""
		return {
			"player1": self.player1.to_dict(),
			"player2": self.player2.to_dict(),
			"ball": {
				"x": self.ball_x,
				"y": self.ball_y,
				"radius": self.ball_radius
			},
			"game_over": self.game_over,
			"winner": self.winner
		}

async def game_loop(game_id: str):
	"""Main game loop that updates ball position"""
	while True:
		if game_id in games and len(games[game_id]["connections"]) > 0:
			game_state = games[game_id]["state"]
			game_state.update_ball()
			
			# Send game state to all connected clients
			state_dict = game_state.to_dict()
			for connection in games[game_id]["connections"]:
				try:
					await connection.send_text(json.dumps(state_dict))
				except:
					pass
					
		await asyncio.sleep(1/60)  # 60 FPS

@app.websocket("/ws/game1")
async def websocket_endpoint(websocket: WebSocket):
	await websocket.accept()
	
	if "game1" not in games:
		data = await websocket.receive_text()
		config = json.loads(data)
		with_ai = config.get('withAI', False)
		difficulty = config.get('difficulty', 0)
		
		games["game1"] = {
			"state": GameState(with_ai=with_ai, difficulty=difficulty),
			"connections": []
		}
		asyncio.create_task(game_loop("game1"))
	
	try:
		games["game1"]["connections"].append(websocket)
		while True:
			data = await websocket.receive_text()
			data = json.loads(data)
			print(f"Received game input: {data}")  # Debug print
			
			if "move" in data:
				player_num = data.get("player")
				direction = data.get("direction")
				
				game_state = games["game1"]["state"]
				print(f"Game state AI status: {game_state.with_ai}")  # Debug print
				
				# Ignoriere Eingaben für Spieler 2 wenn AI aktiv ist
				if game_state.with_ai and player_num == 2:
					continue
					
				if player_num in [1, 2]:
					player = getattr(game_state, f"player{player_num}")
					player.move(direction)
					
	except WebSocketDisconnect:
		print("WebSocket disconnected")
	except Exception as e:
		print(f"Error: {e}")
	finally:
		if websocket in games["game1"]["connections"]:
			games["game1"]["connections"].remove(websocket)
		await websocket.close()
		
		# Wenn keine Verbindungen mehr, Game aufräumen
		if len(games["game1"]["connections"]) == 0:
			games.pop("game1", None)

@app.websocket("/ws/menu")
async def menu_websocket(websocket: WebSocket):
	await websocket.accept()
	
	try:
		# Sende initialen Menüzustand direkt nach Verbindungsaufbau
		await websocket.send_json({
			'type': 'menu_update',
			'state': menu_state.to_dict()
		})
		
		while True:
			data = await websocket.receive_json()
			
			if 'key' in data:
				result = menu_state.handle_input(data['key'])
				if result:
					# Wenn ein Spiel gestartet werden soll
					await websocket.send_json({
						'type': 'start_game',
						'config': result
					})
				else:
					# Sende aktualisierten Menüzustand
					await websocket.send_json({
						'type': 'menu_update',
						'state': menu_state.to_dict()
					})
					
	except WebSocketDisconnect:
		pass

@app.get("/")
async def read_index():
	return FileResponse('index.html')
