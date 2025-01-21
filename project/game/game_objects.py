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