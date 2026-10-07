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
from .npc import NPC, Player, Guard, Civilian, DisguiseData, CharacterData
from .door import Door, DoorSurfaces


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
    npcs: list[NPC]
    doors: list[Door]
    
    


class Game:
    
    def __init__(self, level_path: str, asset_path: str):
        pygame.init()
        
        self.window: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        
        self.level_path: str = level_path
        self.asset_path: str = asset_path
        
        self.level_rooms: dict[str, dict[str, Room]] = {}
        self.room_graph_links: dict[str, dict[str, list[str]]] = {}
                
        if os.path.exists(level_path):
            with open(level_path, "r") as f:
                self.level_data: LevelData = json.load(f)
        else:
            raise FileExistsError("Level not exists.")
        
        self.assets: dict = load_assets(asset_path)
        
        self.player: Player = None
        
        self.initial_setup()
        
        self.run_loop: bool = True
        self.clock: pygame.Clock = pygame.Clock()
        
        self.camera: Camera = Camera()
        
        self.current_floor: str = "0"
        
    def initial_setup(self) -> None:
        for floor_level, floor_data in self.level_data["rooms"].items():
            self.level_rooms[floor_level] = {}
            self.room_graph_links[floor_level] = {}
            
            all_furnitures: list[FurnitureData] = get_from_dict(self.level_data, ["furnitures", floor_level], [])[:]
            all_npcs: list[NPCData] = get_from_dict(self.level_data, ["npc", floor_level], [])[:]
            all_doors: list[DoorData] = get_from_dict(self.level_data, ["doors", floor_level], [])[:]
            
            for room_id, room_data in floor_data.items():
                room_furnitures: list[tuple[FurnitureData, pygame.Surface, pygame.Rect]] = []
                room_npcs: list[NPC] = []
                room_walls: list[pygame.Rect] = []
                
                # Room Surface
                pixel_width: int = room_data["width"] * TILE_SIZE
                pixel_height: int = room_data["height"] * TILE_SIZE
                
                room_position: tuple[int, int] = (room_data["indexes"][0] * TILE_SIZE, room_data["indexes"][1] * TILE_SIZE)
                
                room_surface = pygame.Surface((pixel_width, pixel_height))
                
                wall_surf: pygame.Surface = get_from_dict(self.assets, room_data["wall_tile"].split(os.path.sep), None)
                floor_surf1: pygame.Surface = get_from_dict(self.assets, [*room_data["floor_tile"].split(os.path.sep), "0"], None)
                floor_surf2: pygame.Surface = get_from_dict(self.assets, [*room_data["floor_tile"].split(os.path.sep), "1"], floor_surf1)
                
                # Create room wall collision rects
                top_wall_rect = pygame.Rect(
                    room_position[0],
                    room_position[1],
                    room_data["width"] * TILE_SIZE,
                    TILE_SIZE,
                )
                
                left_wall_rect = pygame.Rect(
                    room_position[0],
                    room_position[1],
                    TILE_SIZE,
                    pixel_height
                )
                
                bottom_wall_rect = pygame.Rect(
                    room_position[0],
                    room_position[1] + (room_data["height"] - 1) * TILE_SIZE,
                    pixel_width,
                    TILE_SIZE
                )
                
                right_wall_rect = pygame.Rect(
                    room_position[0] + (room_data["width"] - 1) * TILE_SIZE,
                    room_position[1],
                    TILE_SIZE,
                    pixel_height
                )
                
                room_walls.extend((top_wall_rect, left_wall_rect, bottom_wall_rect, right_wall_rect))
                
                for i in range(room_data["width"]):
                    for j in range(room_data["height"]):
                        is_wall: bool = (i in [0, room_data["width"] - 1]) or (j in [0, room_data["height"] - 1])
                        
                        tile_surf: pygame.Surface = wall_surf if is_wall else (floor_surf1 if (i + j) % 2 else floor_surf2)
                        
                        room_surface.blit(tile_surf, (i * TILE_SIZE, j * TILE_SIZE))
                        
                # Place furnitures
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
                        all_furnitures.remove(furniture)
                        
                # Place NPC and player
                for npc_data in all_npcs[:]:
                    if (
                        ((room_data["indexes"][0] * TILE_SIZE) <= npc_data["position"][0] <= ((room_data["indexes"][0] + room_data["width"]) * TILE_SIZE))
                        and  
                        ((room_data["indexes"][1] * TILE_SIZE) <= npc_data["position"][1] <= ((room_data["indexes"][1] + room_data["height"]) * TILE_SIZE))
                    ):
                        is_player: bool = npc_data.get("is_player", False)
                        is_guard: bool = npc_data.get("is_guard", False)
                        is_target: bool = npc_data.get("is_target", False)
                        
                        disguise_surfaces: dict[str, pygame.Surface] = get_from_dict(self.assets, npc_data["disguise"].split(os.path.sep), {})
                        
                        disguise_data: DisguiseData = {
                            "name": npc_data["disguise"].split(os.path.sep)[1],
                            **disguise_surfaces
                        }
                        
                        character_surfaces: dict[str, pygame.Surface] = get_from_dict(self.assets, npc_data["type"].split(os.path.sep), {})
                                                
                        character_data: CharacterData = {
                            "name": npc_data["type"].split(os.path.sep)[1],
                            **character_surfaces
                        }
                        
                        # print(disguise_data)
                        
                        NPCClass = Player if is_player else (Guard if is_guard else Civilian)
                        
                        new_npc = NPCClass(
                            self,
                            npc_data["position"][0],
                            npc_data["position"][1],
                            npc_data["rotation"] * 90,
                            disguise=disguise_data,
                            character=character_data,
                            is_target=is_target,
                            room_id=room_id
                        )
                        
                        if is_player and self.player is None:
                            self.player = new_npc
                        else:
                            room_npcs.append(new_npc)
                        
                        all_npcs.remove(npc_data)
                
                room: Room = {
                    "room_id": room_id,
                    **room_data,
                    "pixel_width": pixel_width,
                    "pixel_height": pixel_height,
                    "furnitures": room_furnitures,
                    "surface": room_surface,
                    "walls": room_walls,
                    "position": room_position,
                    "npcs": room_npcs,
                    "doors": []
                }
                
                self.level_rooms[floor_level][room_id] = room
                
            # Place Doors
            for door_data in all_doors:
                
                door_x, door_y = door_data["indexes"][0] * TILE_SIZE, door_data["indexes"][1] * TILE_SIZE
                
                room_1_id: str = door_data["neighbors_rooms"][0]
                room_1_left: int = door_data["neighbors_tiles"][0][0] * TILE_SIZE
                room_1_top: int = door_data["neighbors_tiles"][0][1] * TILE_SIZE
                
                room_1_width: int = door_data["neighbors_tiles"][1][0] * TILE_SIZE - room_1_left
                room_1_height: int = door_data["neighbors_tiles"][1][1] * TILE_SIZE - room_1_top
                
                room_1_trigger_rect: pygame.Rect = pygame.Rect(
                    room_1_left,
                    room_1_top,
                    room_1_width,
                    room_1_height
                )
                
                room_2_id: str = door_data["neighbors_rooms"][1]
                room_2_left: int = door_data["neighbors_tiles"][2][0] * TILE_SIZE
                room_2_top: int = door_data["neighbors_tiles"][2][1] * TILE_SIZE
                
                room_2_width: int = door_data["neighbors_tiles"][3][0] * TILE_SIZE - room_2_left
                room_2_height: int = door_data["neighbors_tiles"][3][1] * TILE_SIZE - room_2_top
                
                room_2_trigger_rect: pygame.Rect = pygame.Rect(
                    room_2_left,
                    room_2_top,
                    room_2_width,
                    room_2_height
                )
                
                trigger_rects: dict[str, pygame.Rect] = {
                    room_1_id: room_1_trigger_rect,
                    room_2_id: room_2_trigger_rect,
                }
                
                door_surf: pygame.Surface = get_from_dict(self.assets, door_data["asset"].split(os.path.sep), None)
                floor_surf: pygame.Surface = get_from_dict(self.assets, self.level_rooms[floor_level][room_1_id]["floor_tile"].split(os.path.sep), None)
                
                door_surfaces: DoorSurfaces = {
                    "door_surface": door_surf,
                    "floor_surface": floor_surf
                }
                
                new_door = Door(
                    self,
                    x=door_x,
                    y=door_y,
                    rotation=door_data["rotation"],
                    surfaces=door_surfaces,
                    trigger_rects=trigger_rects
                )
                
                self.level_rooms[floor_level][room_1_id]["doors"].append(new_door)
                self.level_rooms[floor_level][room_2_id]["doors"].append(new_door)

                # Generate room graph links
                if self.room_graph_links[floor_level].get(room_1_id, None) is None:
                    self.room_graph_links[floor_level][room_1_id] = []
                    
                if self.room_graph_links[floor_level].get(room_2_id, None) is None:
                    self.room_graph_links[floor_level][room_2_id] = []
                    
                self.room_graph_links[floor_level][room_1_id].append(room_2_id)
                self.room_graph_links[floor_level][room_2_id].append(room_1_id)
        
        self.current_floor = "0"
        
        # print(self.level_rooms["0"]["0"])
        # print(self.room_graph_links["0"])
        
    def manage_npcs(self) -> None:
        for room in self.level_rooms[self.current_floor].values():
            for npc in room["npcs"]:
                npc.update()
        
        
    def draw(self) -> None:
        self.window.fill(BACKGROUND_COLOR)
        self.draw_rooms(draw_collisions=False)
        self.draw_npcs()
        
    def draw_npcs(self) -> None:
        for room in self.level_rooms[self.current_floor].values():
            for npc in room["npcs"]:
                npc.draw()
                
        self.player.draw()
    
    def draw_rooms(self, draw_collisions: bool = False) -> None:
        
        floor_rooms = self.level_rooms[self.current_floor]
        
        for room in floor_rooms.values():
            self.window.blit(room["surface"], self.camera.convert_pos(room["position"]))
            
            if draw_collisions:
                for wall_rect in room["walls"]:
                    wall_rect = wall_rect.copy()
                    wall_rect.topleft = self.camera.convert_pos(wall_rect.topleft)
                    pygame.draw.rect(self.window, "red", wall_rect, width=2)
                    
                for _, __, furniture_rect in room["furnitures"]:
                    furniture_rect.topleft = self.camera.convert_pos(furniture_rect.topleft)
                    pygame.draw.rect(self.window, "red", furniture_rect, width=2)
                    
    def update(self) -> None:
        self.manage_npcs()
        
    def run(self) -> None:
        while self.run_loop:
                    
            all_events: list[pygame.Event] = pygame.event.get()
            
            key_pressed = pygame.key.get_pressed()
            
            for event in all_events:
                if event.type == pygame.QUIT or ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE)):
                    self.run_loop = False
                    
            self.update()
            
            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)