import time
import random
from dataclasses import dataclass

@dataclass
class Ball:
    x: float
    y: float
    dx: float
    dy: float

@dataclass
class Paddle:
    x: float
    y: float
    height: float

class AI:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty
        self.target_y = 0
        self.last_calculation = 0
        
        # Delay in milliseconds for each difficulty
        self.delays = {
            0: 0.150,  # Easy: 150ms delay
            1: 0.080,  # Medium: 80ms delay
            2: 0.020   # Hard: 20ms delay
        }
        
        # Movement speeds for each difficulty
        self.speeds = {
            0: 3,  # Easy
            1: 5,  # Medium
            2: 7   # Hard
        }

    def calculate_next_move(self, ball: Ball, paddle: Paddle, canvas_height: int) -> float:
        """
        Calculate the next position where the AI paddle should move to.
        Returns the target Y position.
        """
        current_time = time.time()
        
        # Only calculate new position after delay has passed
        if current_time - self.last_calculation < self.delays[self.difficulty]:
            return self.target_y
            
        self.last_calculation = current_time

        # Predict where the ball will intersect with paddle's x position
        future_y = self.predict_ball_position(ball, paddle, canvas_height)
        
        # Add randomness for easier difficulties
        if self.difficulty == 0:  # Easy
            future_y += (random.random() - 0.5) * 50
        elif self.difficulty == 1:  # Medium
            future_y += (random.random() - 0.5) * 25

        # Ensure paddle stays within canvas bounds
        half_paddle_height = paddle.height / 2
        future_y = max(half_paddle_height, min(canvas_height - half_paddle_height, future_y))

        self.target_y = future_y
        return self.target_y

    def predict_ball_position(self, ball: Ball, paddle: Paddle, canvas_height: int) -> float:
        """
        Predict where the ball will intersect with the paddle's X position.
        Returns the predicted Y position.
        """
        # Copy ball properties to predict trajectory
        predicted_x = ball.x
        predicted_y = ball.y
        dx = ball.dx
        dy = ball.dy
        paddle_x = paddle.x

        # Simulate ball movement until it reaches paddle's X position
        while predicted_x < paddle_x:
            predicted_x += dx
            predicted_y += dy

            # Bounce off top and bottom walls
            if predicted_y <= 0 or predicted_y >= canvas_height:
                dy = -dy

        return predicted_y

    def get_move_direction(self, current_y: float, target_y: float) -> float:
        """
        Determine the direction and speed the paddle should move.
        Returns the movement amount (positive for down, negative for up).
        """
        threshold = 5  # Dead zone to prevent jittering
        
        if abs(current_y - target_y) < threshold:
            return 0  # Don't move if very close to target
        
        speed = self.speeds[self.difficulty]
        
        if current_y < target_y:
            return speed  # Move down
        else:
            return -speed  # Move up

    def update(self, ball: Ball, paddle: Paddle, canvas_height: int) -> float:
        """
        Main update method to be called from the game loop.
        Returns the new Y position for the paddle.
        """
        target_y = self.calculate_next_move(ball, paddle, canvas_height)
        move_amount = self.get_move_direction(
            paddle.y + paddle.height/2,
            target_y
        )
        
        new_y = paddle.y + move_amount
        
        # Ensure paddle stays within bounds
        new_y = max(0, min(canvas_height - paddle.height, new_y))
        
        return new_y 