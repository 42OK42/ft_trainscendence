from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
from player import Player  # Fixed import statement
import random
import math
from ai_player import AI  # neue Import

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Player dictionary for active games
games = {}

class GameState:
	def __init__(self, with_ai=False, difficulty=0):
		self.player1 = Player(is_left_player=True)
		self.player2 = Player(is_left_player=False)
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

		# Wenn AI aktiv ist, ignoriere Eingaben für Spieler 2
		if self.with_ai and player_id == 2:
			return

		if player_id == 1:
			player = self.player1
		else:
			player = self.player2

		if input_data.get("up"):
			player.move_up()
		if input_data.get("down"):
			player.move_down()

	def update_ball(self):
		"""Updates ball position and handles collisions"""
		if self.game_over:
			return

		# Update AI if active
		if self.with_ai:
			ball = Ball(self.ball_x, self.ball_y, self.ball_dx, self.ball_dy)
			paddle = Paddle(self.player2.x, self.player2.y, self.player2.height)
			new_y = self.ai.update(ball, paddle, 500)  # 500 ist canvas height
			self.player2.y = new_y

		self.ball_x += self.ball_dx
		self.ball_y += self.ball_dy
		
		# Wall collisions (top and bottom)
		if self.ball_y <= 0 or self.ball_y >= 500:
			self.ball_dy *= -1
			
		# Paddle collisions
		for player in [self.player1, self.player2]:
			if (player.x < self.ball_x < player.x + player.width and
				player.y < self.ball_y < player.y + player.height):
				self.ball_dx *= -1
				# Add a bit of randomness to y direction
				self.ball_dy += random.uniform(-1, 1)
				# Normalize speed
				speed = math.sqrt(self.ball_dx**2 + self.ball_dy**2)
				self.ball_dx = (self.ball_dx/speed) * self.ball_speed
				self.ball_dy = (self.ball_dy/speed) * self.ball_speed
				
		# Score points
		if self.ball_x <= 0:
			self.player2.increase_score()
			self.check_winner()  # Check for winner after score
			self.reset_ball()
		elif self.ball_x >= 800:
			self.player1.increase_score()
			self.check_winner()  # Check for winner after score
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
		# Empfange die Spielkonfiguration
		data = await websocket.receive_text()
		config = json.loads(data)
		with_ai = config.get('withAI', False)
		difficulty = config.get('difficulty', 0)
		
		games["game1"] = {
			"state": GameState(with_ai, difficulty),
			"connections": []
		}
		asyncio.create_task(game_loop("game1"))
	
	games["game1"]["connections"].append(websocket)
	
	try:
		while True:
			data = await websocket.receive_text()
			data = json.loads(data)
			
			if "move" in data:
				player_num = data.get("player")
				direction = data.get("direction")
				
				if player_num in [1, 2]:
					player = getattr(games["game1"]["state"], f"player{player_num}")
					player.move(direction)
					
	except Exception as e:
		print(f"Error: {e}")
	finally:
		games["game1"]["connections"].remove(websocket)

@app.get("/")
async def read_index():
	return FileResponse('index.html')
