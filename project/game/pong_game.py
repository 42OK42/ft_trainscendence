from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class PongGame:
    def __init__(self):
        self.ball_x = 400
        self.ball_y = 300
        self.ball_speed_x = 5
        self.ball_speed_y = 3
        self.paddle1_y = 250
        self.paddle2_y = 250
        self.score1 = 0
        self.score2 = 0
        self.paddle_speed = 10
        self.paddle_height = 100
        self.last_update = 0
        self.frame_time = 1/60  # 60 FPS

    def move_paddle(self, paddle, direction):
        if paddle == 1:
            self.paddle1_y += direction * self.paddle_speed
            self.paddle1_y = max(0, min(500, self.paddle1_y))
        else:
            self.paddle2_y += direction * self.paddle_speed
            self.paddle2_y = max(0, min(500, self.paddle2_y))

    def update(self, current_time):
        # Check if enough time has passed since last update
        if current_time - self.last_update < self.frame_time:
            return
        
        self.last_update = current_time

        # Ball movement with constant speed
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # Collision with top and bottom walls
        if self.ball_y <= 0 or self.ball_y >= 600:
            self.ball_speed_y *= -1

        # Collision with paddles
        if self.ball_x <= 60 and self.paddle1_y <= self.ball_y <= self.paddle1_y + self.paddle_height:
            self.ball_speed_x *= -1
        if self.ball_x >= 730 and self.paddle2_y <= self.ball_y <= self.paddle2_y + self.paddle_height:
            self.ball_speed_x *= -1

        # Score points and reset ball
        if self.ball_x <= 0:
            self.score2 += 1
            self.reset_ball()
        elif self.ball_x >= 800:
            self.score1 += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball_x = 400
        self.ball_y = 300
        self.ball_speed_x *= -1

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    print(f"New WebSocket connection: {game_id}")
    await websocket.accept()
    game = PongGame()
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=0.016)
                message = json.loads(data)
                
                # Paddle controls
                if message['action'] == 'PADDLE1_UP':
                    game.move_paddle(1, -1)
                elif message['action'] == 'PADDLE1_DOWN':
                    game.move_paddle(1, 1)
                elif message['action'] == 'PADDLE2_UP':
                    game.move_paddle(2, -1)
                elif message['action'] == 'PADDLE2_DOWN':
                    game.move_paddle(2, 1)
                    
            except asyncio.TimeoutError:
                pass

            # Update with timestamp
            current_time = asyncio.get_event_loop().time()
            game.update(current_time)
            
            game_state = {
                "ball_x": game.ball_x,
                "ball_y": game.ball_y,
                "paddle1_y": game.paddle1_y,
                "paddle2_y": game.paddle2_y,
                "score1": game.score1,
                "score2": game.score2
            }
            await websocket.send_json(game_state)
            
            # Fixed frame rate
            await asyncio.sleep(0.016)  # ~60 FPS
    except Exception as e:
        print(f"Error: {e}")

@app.get("/")
async def read_index():
    return FileResponse('index.html')
