from fastapi import FastAPI, WebSocket
from menu import Menu
from game_server import GameServer
import uuid

app = FastAPI()
menu = Menu()
game_server = GameServer()

@app.websocket("/ws/menu")
async def websocket_menu(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "get_menu_items":
                menu_items = await menu.get_menu_items()
                await websocket.send_json({"menu_items": menu_items})
            
            elif data["action"] == "menu_selection":
                response = await menu.handle_menu_selection(websocket, data["selection"])
                await websocket.send_json(response)
                
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close()

@app.websocket("/ws/game/{game_id}")
async def websocket_game(websocket: WebSocket, game_id: str):
    await game_server.handle_game(websocket, game_id, menu.settings) 