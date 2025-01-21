class Player:
    def __init__(self, is_left_player: bool):
        self.y = 250  # Starting position in the middle
        self.height = 100
        self.width = 10
        self.speed = 5
        self.is_left_player = is_left_player
        self.x = 50 if is_left_player else 740  # Position left or right
        self.score = 0
        
    def move(self, direction: int) -> None:
        """
        Moves the player up or down
        :param direction: -1 for up, 1 for down
        """
        new_y = self.y + (direction * self.speed)
        if 0 <= new_y <= 400:  # 500 - paddle_height for max position
            self.y = new_y
            
    def increase_score(self) -> None:
        """Increases the player's score by 1"""
        self.score += 1
        
    def reset_position(self) -> None:
        """Resets the player's position"""
        self.y = 250
        
    def to_dict(self) -> dict:
        """Converts player data to dictionary for JSON transmission"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "score": self.score,
            "is_left_player": self.is_left_player
        } 