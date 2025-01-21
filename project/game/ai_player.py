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
        self.speeds = {
            0: 3,  # Easy
            1: 5,  # Medium 
            2: 7   # Hard
        }

    def update(self, ball, paddle, canvas_height):
        """Berechnet die nächste Position für das AI-Paddle"""
        # Berechne Zielposition
        target_y = self.predict_ball_position(ball, paddle, canvas_height)
        
        # Bewege das Paddle zur Zielposition
        current_y = paddle.y + paddle.height/2  # Paddlemitte
        speed = self.speeds[self.difficulty]
        
        # Deadzone um Zittern zu vermeiden
        if abs(current_y - target_y) < 5:
            return paddle.y
            
        # Bewege hoch oder runter
        if current_y < target_y:
            new_y = paddle.y + speed
        else:
            new_y = paddle.y - speed
            
        # Stelle sicher, dass das Paddle im Spielfeld bleibt
        return max(0, min(canvas_height - paddle.height, new_y))

    def predict_ball_position(self, ball, paddle, canvas_height):
        """Berechnet wo der Ball das Paddle treffen wird"""
        # Wenn der Ball sich vom Paddle wegbewegt, ziele auf die Mitte
        if ball.dx < 0:
            return canvas_height / 2
            
        # Berechne Auftreffpunkt
        predicted_x = ball.x
        predicted_y = ball.y
        dx = ball.dx
        dy = ball.dy

        # Verfolge den Ball bis er das Paddle erreicht
        while predicted_x < paddle.x:
            predicted_x += dx
            predicted_y += dy
            
            # Prüfe Kollision mit oberer/unterer Wand
            if predicted_y <= 0 or predicted_y >= canvas_height:
                dy = -dy

        return predicted_y 