class Player:
    def __init__(self, is_left_player: bool, is_ai: bool = False):
        self.is_left_player = is_left_player
        self.is_ai = is_ai
        self.x = 50 if is_left_player else 740
        self.height = 100
        self.width = 10
        self.speed = 5
        self.score = 0
        self.reset()  # Initialisiere Position
        
    def reset(self):
        """Reset player position and score"""
        self.y = 250  # Reset to middle position
        self.score = 0
        
    def move(self, direction: int) -> None:
        """
        Moves the player up or down
        :param direction: -1 for up, 1 for down
        """
        # Wenn AI, dann keine manuelle Bewegung
        if self.is_ai:
            return
            
        new_y = self.y + (direction * self.speed)
        if 0 <= new_y <= 400:  # 500 - paddle_height for max position
            self.y = new_y
            
    def increase_score(self) -> None:
        """Increases the player's score by 1"""
        self.score += 1
        
    def to_dict(self) -> dict:
        """Converts player data to dictionary for JSON transmission"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "score": self.score,
            "is_left_player": self.is_left_player,
            "is_ai": self.is_ai
        } 