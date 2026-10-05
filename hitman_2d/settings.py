from typing import TypedDict, Optional

SCREEN_SIZE = (0, 0)
# SCREEN_SIZE = (800, 600)
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
        # "create_furniture": {
        #     "type": "button",
        #     "label": "+ Create Furniture",
        #     "text": ""
        # },
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
    "door": {
        "door_assets": {
            "type": "assets",
            "label": "Doors",
            "path": ["Doors"]
        }
    },
    "player": {},
    "npc": {
        "npc_disguises": {
            "type": "assets",
            "label": "Disguise",
            "path": ["Disguises"],
            "filter": {
                "type": "equal",
                "value": "torso"
            }
        },
        "npc_character": {
            "type": "assets",
            "label": "Character",
            "path": ["Characters"],
            "filter": {
                "type": "equal",
                "value": "face"
            }
        },
        
        "is_target": {
            "type": "checkbox",
            "label": "Is target",
            "default_value": False
        },
       
       "is_player": {
            "type": "checkbox",
            "label": "Is player",
            "default_value": False
        },
       
       "is_guard": {
            "type": "checkbox",
            "label": "Is guard",
            "default_value": False
        }  
    },
    "npc_path": {},
    "exit": {}
}


class RoomData(TypedDict):
    indexes: list[int, int]
    wall_tile: str
    floor_tile: str
    floor: int
    width: int
    height: int
    room_id: str
    
    
class FurnitureData(TypedDict):
    indexes: list[int, int]
    asset: str
    rotation: int


class DoorData(TypedDict):
    indexes: list[int, int]
    asset: str
    rotation: int
    door_tiles: list[list[int, int]]
    neighbors_tiles: list[list[int, int]]
    neighbors_rooms: list[str, str]

class NPCData(TypedDict):
    position: list[int, int]
    type: str
    disguise: str
    rotation: int
    is_target: Optional[bool]
    is_player: Optional[bool]
    is_guard: Optional[bool]
    

class LevelData(TypedDict):
    rooms: dict[str, dict[str, RoomData]]
    doors: dict[str, list[DoorData]]
    furnitures: dict[str, list[FurnitureData]]
    npc: dict[str, list[NPCData]]