from fastapi import FastAPI, WebSocket
import json

class Menu:
    def __init__(self):
        self.current_menu_stack = []
        self.menu_items = [
            {"id": "start", "text": "Start Game"},
            {"id": "settings", "text": "Settings"},
            {"id": "leaderboard", "text": "Leaderboard"}
        ]
        
        self.game_mode_items = [
            {"id": "tournament", "text": "Tournament"},
            {"id": "single_game", "text": "Single Game"},
            {"id": "back", "text": "Back"}
        ]
        
        self.play_mode_items = [
            {"id": "local", "text": "Local Multiplayer"},
            {"id": "ai", "text": "Play vs AI"},
            {"id": "online", "text": "Online Multiplayer"},
            {"id": "back", "text": "Back"}
        ]
        
        self.ai_difficulty_items = [
            {"id": "easy", "text": "Easy"},
            {"id": "medium", "text": "Medium"},
            {"id": "impossible", "text": "Impossible"},
            {"id": "back", "text": "Back"}
        ]

        self.settings = {
            "ball_speed": 5,
            "paddle_speed": 5,
            "winning_score": 5,
            "paddle_size": "middle"
        }

    async def handle_menu_selection(self, websocket: WebSocket, selection: str):
        if selection == "start":
            self.current_menu_stack.append("main")
            return {"action": "show_submenu", "menu_items": self.game_mode_items}
        
        elif selection == "settings":
            return {
                "action": "show_settings",
                "settings": self.settings
            }
            
        elif selection in ["tournament", "single_game"]:
            self.current_menu_stack.append("game_mode")
            return {"action": "show_submenu", "menu_items": self.play_mode_items, "selected_mode": selection}
            
        elif selection == "local":
            return {"action": "start_game", "mode": "local"}
            
        elif selection == "ai":
            self.current_menu_stack.append("play_mode")
            return {"action": "show_submenu", "menu_items": self.ai_difficulty_items}
            
        elif selection in ["easy", "medium", "impossible"]:
            return {"action": "start_game", "mode": "ai", "difficulty": selection}
            
        elif selection == "back":
            if self.current_menu_stack:
                last_menu = self.current_menu_stack.pop()
                if last_menu == "main":
                    return {"action": "show_main_menu", "menu_items": self.menu_items}
                elif last_menu == "game_mode":
                    return {"action": "show_submenu", "menu_items": self.game_mode_items}
                elif last_menu == "play_mode":
                    return {"action": "show_submenu", "menu_items": self.play_mode_items}
            return {"action": "show_main_menu", "menu_items": self.menu_items}
            
        elif selection == "leaderboard":
            return {"action": "show_leaderboard"}
            
        elif selection == "exit":
            return {"action": "exit_game"}

    async def update_settings(self, settings_data):
        try:
            ball_speed = int(settings_data.get("ball_speed", 5))
            paddle_speed = int(settings_data.get("paddle_speed", 5))
            winning_score = int(settings_data.get("winning_score", 5))
            paddle_size = settings_data.get("paddle_size", "middle")
            
            if paddle_size not in ["small", "middle", "big"]:
                paddle_size = "middle"
                
            if (1 <= ball_speed <= 10 and 
                1 <= paddle_speed <= 10 and 
                1 <= winning_score <= 20):
                
                self.settings = {
                    "ball_speed": ball_speed,
                    "paddle_speed": paddle_speed,
                    "winning_score": winning_score,
                    "paddle_size": paddle_size
                }
                return {"action": "settings_updated", "settings": self.settings}
            else:
                return {"action": "settings_error", "message": "Values must be between 1 and 10"}
        except ValueError:
            return {"action": "settings_error", "message": "Invalid input values"}

    async def get_menu_items(self):
        return self.menu_items 

    def display_settings(self, settings):
        # This method is not provided in the original file or the code block
        # It's assumed to exist as it's called in the code block
        # Implementation of display_settings method
        pass 