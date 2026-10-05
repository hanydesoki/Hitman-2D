import os
import json

import pygame

from .utilities import (
    load_assets, 
    get_from_dict,
    set_to_dict,
    find_all_element_from_type,
    generate_unique_id
)

from .settings import *
from .camera import Camera


class Room(TypedDict):
    room_id: str
    indexes: list[int, int]
    wall_tile: str
    floor_tile: str
    floor: int
    width: int
    height: int
    position: list[int, int]
    pixel_width: int
    pixel_height: int
    surface: pygame.Surface
    walls: list[pygame.Rect]
    furnitures: list[tuple[FurnitureData, pygame.Surface, pygame.Rect]]
    
    


class Game:
    
    def __init__(self, level_path: str, asset_path: str):
        pygame.init()
        
        self.window: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        
        self.level_path: str = level_path
        self.asset_path: str = asset_path
        
        self.level_rooms: dict[str, dict[str, Room]] = {}
                
        if os.path.exists(level_path):
            with open(level_path, "r") as f:
                self.level_data: LevelData = json.load(f)
        else:
            raise FileExistsError("Level not exists.")
        
        self.assets: dict = load_assets(asset_path)
        
        self.initial_setup()
        
        self.run_loop: bool = True
        self.clock: pygame.Clock = pygame.Clock()
        
        self.camera: Camera = Camera()
        
        self.current_floor: str = "0"
        
    def initial_setup(self) -> None:
        for floor_level, floor_data in self.level_data["rooms"].items():
            self.level_rooms[floor_level] = {}
            
            all_furnitures: list[FurnitureData] = get_from_dict(self.level_data, ["furnitures", floor_level], [])[:]
            
            for room_id, room_data in floor_data.items():
                room_furnitures: list[tuple[FurnitureData, pygame.Surface, pygame.Rect]] = []
                room_walls: list[pygame.Rect] = []
                
                # Room Surface
                pixel_width: int = room_data["width"] * TILE_SIZE
                pixel_height: int = room_data["height"] * TILE_SIZE
                
                room_position: tuple[int, int] = (room_data["indexes"][0] * TILE_SIZE, room_data["indexes"][1] * TILE_SIZE)
                
                room_surface = pygame.Surface((pixel_width, pixel_height))
                
                wall_surf: pygame.Surface = get_from_dict(self.assets, room_data["wall_tile"].split(os.path.sep), None)
                floor_surf1: pygame.Surface = get_from_dict(self.assets, [*room_data["floor_tile"].split(os.path.sep), "0"], None)
                floor_surf2: pygame.Surface = get_from_dict(self.assets, [*room_data["floor_tile"].split(os.path.sep), "1"], floor_surf1)
                
                for i in range(room_data["width"]):
                    for j in range(room_data["height"]):
                        is_wall: bool = (i in [0, room_data["width"] - 1]) or (j in [0, room_data["height"] - 1])
                        
                        tile_surf: pygame.Surface = wall_surf if is_wall else (floor_surf1 if (i + j) % 2 else floor_surf2)
                        
                        room_surface.blit(tile_surf, (i * TILE_SIZE, j * TILE_SIZE))
                        
                
                for furniture in all_furnitures[:]:
                    if (
                        (room_data["indexes"][0] <= furniture["indexes"][0] <= room_data["indexes"][0] + room_data["width"])
                        and  
                        (room_data["indexes"][1] <= furniture["indexes"][1] <= room_data["indexes"][1] + room_data["height"])
                    ):  
                        
                        furniture_position: list[int, int] = (furniture["indexes"][0] * TILE_SIZE, furniture["indexes"][1] * TILE_SIZE)
                        
                        furniture_surf: pygame.Surface = pygame.transform.rotate(
                            get_from_dict(self.assets, furniture["asset"].split(os.path.sep), None), 
                            furniture["rotation"] * 90
                        )
                        
                        furniture_surf.set_colorkey("white")
                        
                        furniture_rect = furniture_surf.get_rect(topleft=furniture_position)

                        room_furnitures.append((furniture, furniture_surf, furniture_rect))
                        
                        relative_furniture_position: tuple[int, int] = (
                            furniture_position[0] - room_position[0], 
                            furniture_position[1] - room_position[1]
                        )
                        
                        room_surface.blit(furniture_surf, relative_furniture_position)
                        
                        
                room: Room = {
                    "room_id": room_id,
                    **room_data,
                    "pixel_width": pixel_width,
                    "pixel_height": pixel_height,
                    "furnitures": room_furnitures,
                    "surface": room_surface,
                    "walls": room_walls,
                    "position": room_position
                }
                
                # print(room)
                
                self.level_rooms[floor_level][room_id] = room
                
        # TODO: Place NPC and player
        
        self.current_floor = "0"
        # print(self.level_rooms)
        
    def draw(self) -> None:
        self.window.fill(BACKGROUND_COLOR)
        self.draw_rooms()
    
    def draw_rooms(self) -> None:
        
        floor_rooms = self.level_rooms[self.current_floor]
        
        for room in floor_rooms.values():
            self.window.blit(room["surface"], self.camera.convert_pos(room["position"]))
        
    def run(self) -> None:
        while self.run_loop:
                    
            all_events: list[pygame.Event] = pygame.event.get()
            
            key_pressed = pygame.key.get_pressed()
            
            for event in all_events:
                if event.type == pygame.QUIT or ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE)):
                    self.run_loop = False
            
            self.draw()
            pygame.display.update()