SCREEN_SIZE = (0, 0)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_SIZE

FPS = 60


# LEVEL_CREATOR 
LEFT_SIDEBAR_MENU_WIDTH = 300
RIGTH_SIDEBAR_MENU_WIDTH = 200
BACKGROUND_COLOR = (50, 50, 50)
SIDEBAR_BACKGROUND_COLOR = (100, 100, 100)

TILE_SIZE = 40


MENU_LAYOUT: dict[str, dict[str, dict]] = {
    "room": {
        "create_room": {
            "type": "button",
            "label": "+ Create Room",
            "text": ""
        },
        "delete_room": {
            "type": "button",
            "label": "-  Delete Room",
            "text": ""
        },
        "room_walls": {
            "type": "assets",
            "label": "Walls",
            "path": ["Walls"]
        },
        "room_floor": {
            "type": "assets",
            "label": "Floor",
            "path": ["Floor_Tiles"]
        } 
    },
    "tiles": {},
    
    "furniture": {
        "create_furniture": {
            "type": "button",
            "label": "+ Create Furniture",
            "text": ""
        },
        # "delete_furniture": {
        #     "type": "button",
        #     "label": "-  Delete Furniture",
        #     "text": ""
        # },
        "decoration": {
            "type": "assets",
            "label": "Decorations",
            "path": ["Furnitures", "Decorations"]
        },
        "containers": {
            "type": "assets",
            "label": "Containers",
            "path": ["Furnitures", "Containers"]
        }
    },
    
    "player": {},
    "npc": {},
    "npc_path": {},
    "exit": {}
}