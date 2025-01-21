class MenuState:
    def __init__(self):
        self.current_state = 'main'  # 'main' oder 'difficulty'
        self.selected_option = 0
        self.selected_difficulty = 0
        self.difficulties = ['Easy', 'Medium', 'Hard']

    def handle_input(self, key: str):
        """Verarbeitet Tasteneingaben für das Menü"""
        if self.current_state == 'main':
            if key == 'ArrowUp':
                self.selected_option = 0
            elif key == 'ArrowDown':
                self.selected_option = 1
            elif key == 'Enter':
                if self.selected_option == 0:
                    return {'action': 'start_game', 'withAI': False}
                else:
                    self.current_state = 'difficulty'
        
        elif self.current_state == 'difficulty':
            if key == 'ArrowUp':
                self.selected_difficulty = (self.selected_difficulty - 1) % 3
            elif key == 'ArrowDown':
                self.selected_difficulty = (self.selected_difficulty + 1) % 3
            elif key == 'Enter':
                return {
                    'action': 'start_game',
                    'withAI': True,
                    'difficulty': self.selected_difficulty
                }
            elif key == 'Escape':
                self.current_state = 'main'

        return None

    def to_dict(self):
        """Konvertiert den Menüzustand in ein Dictionary"""
        return {
            'current_state': self.current_state,
            'selected_option': self.selected_option,
            'selected_difficulty': self.selected_difficulty,
            'difficulties': self.difficulties
        } 