import os
import json
from typing import Any

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
from .button import Button
from .segmented_control import SegmentedControl
from .text_display import TextDisplay
from .selectable_asset import SelectableAsset
from .json_editor import JSONEditor
from .text_field import TextField


class LevelCreator:
    
    def __init__(self, level_path: str, asset_path: str):
        pygame.init()
        
        self.window: pygame.Surface = pygame.display.set_mode(SCREEN_SIZE)
        
        self.level_path: str = level_path
        self.asset_path: str = asset_path
        
        self.level_data: dict = {}
        
        if os.path.exists(level_path):
            with open(level_path, "r") as f:
                self.level_data = json.load(f)
                
        self.assets: dict = load_assets(asset_path)
        
        self.run_loop: bool = True
        self.clock: pygame.Clock = pygame.Clock()
        
        self.camera: Camera = Camera()
        
        self.fonts: dict[str, pygame.Font] = {
            "debug": pygame.font.SysFont("Arial", 25)
        }
        
        # Menu side menu layout
        self.save_button = Button(
            x=10,
            y=10,
            key="save",
            label="Save"
        )
        
        # Switch mode menu
        self.menu_control = SegmentedControl(
            options={
                "room": "Room",
                "door": "Door",
                "tiles": "Tiles",
                "furniture": "Furniture",
                "player": "Player",
                "npc": "NPC",
                "npc_path": "NPC Path",
                "exit": "Exit"
                
            },
            x=10,
            y=self.save_button.rect.bottom + 10,
            key="menu_mode",
            label="Mode",
            allow_multiselect=False,
            require_selection=True,
            max_width=LEFT_SIDEBAR_MENU_WIDTH - 20
        )
        
        self.current_floor: int = 0

        self.floor_up = Button(
            x=10,
            y=self.menu_control.bottom + 10,
            key="up_floor",
            label="Floor +"
        )
        
        self.floor_down = Button(
            x=self.floor_up.rect.right + 10,
            y=self.menu_control.bottom + 10,
            key="down_floor",
            label="Floor -"
        )
        
        # Mode Layout
        self.menu_layout: dict[str, list] = {}
        self.setup_menu_layout()
        
        # Room menu states
        self.selected_room_wall: str = None
        self.selected_room_floor: str = None
        self.room_width: int = 3
        self.room_height: int = 3
        self.is_placing_room: bool = False
        self.selected_room_id: str | None = None
        self.valid_room_placement: bool = False
        
        # Furniture menu states
        self.selected_furniture: dict = None
        self.is_placing_furniture: bool = False
        self.selected_furniture_asset: str = None
        
        # Door menu states
        self.selected_door: dict = None
        self.is_placing_door: bool = False
        self.selected_door_asset: str  = None
        
        self.json_editor: JSONEditor | None = JSONEditor(
            {
                "name": "John",
                "type": "civilian"
            },
            x=self.screen_width - RIGTH_SIDEBAR_MENU_WIDTH + 10,
            y=10,
            width=RIGTH_SIDEBAR_MENU_WIDTH - 20,
            key="params"
        )
    
    def setup_menu_layout(self) -> None:
        self.menu_layout: dict[str, list] = {}
        
        for menu_key, menu_widgets in MENU_LAYOUT.items():
            self.menu_layout[menu_key] = []
            top: int = self.floor_down.bottom + 20
            
            for widget_key, widget_infos in menu_widgets.items():
                # print(widget_key, widget_infos)
                widget_type: str = widget_infos["type"]
                
                if widget_type == "button":
                    text: str = widget_infos.get("text", "")
                    label: str = widget_infos.get("label", "")
                    text_display = TextDisplay(
                       text, 10,
                       top 
                    )
                    button = Button(
                        text_display.right + 10,
                        top,
                        key=widget_key,
                        label=label
                    )
                    
                    self.menu_layout[menu_key].extend([text_display, button])
                    
                    top = max(text_display.bottom, button.bottom) + 10
                    
                elif widget_type == "assets":
                    label: str = widget_infos.get("label", "")
                    asset_path: list[str] = widget_infos["path"]
                    assets = get_from_dict(self.assets, asset_path, {})
                    surfaces: dict[str, pygame.Surface] = {
                        os.path.join(*asset_path, k): s 
                        for k, s in find_all_element_from_type(assets, [pygame.Surface]).items()
                    }
                    text_display = TextDisplay(label, 10, top, size=20)
                    self.menu_layout[menu_key].append(text_display)
                    top = text_display.bottom + 20
                    left = 10
                    for surf_key, surf in surfaces.items():
                        
                        if left + surf.get_width() + 10 > LEFT_SIDEBAR_MENU_WIDTH:
                            left = 10
                            top += surf.get_height() + 10
                            
                        selectable_asset = SelectableAsset(
                            x=left,
                            y=top,
                            surf=surf,
                            key=surf_key,
                            colorkey="white"
                        )
                        self.menu_layout[menu_key].append(selectable_asset)
                        
                        left += surf.get_width() + 10     
                                       
                    top += surf.get_height() + 20
        
    def convert_game_pos(self, pos: tuple[int, int]) -> tuple[int, int]:
        """
        Convert any position from the level render screen to the window screen.
        It takes account of the sidebar menus.
        """
        return pos[0] + LEFT_SIDEBAR_MENU_WIDTH, pos[1]
    
    def screen_mouse_pos(self) -> tuple[int, int] | None:
        mouse_pos = pygame.mouse.get_pos()
        render_mouse_pos = mouse_pos[0] - LEFT_SIDEBAR_MENU_WIDTH, mouse_pos[1]
        
        if LEFT_SIDEBAR_MENU_WIDTH < mouse_pos[0] < self.screen_width - RIGTH_SIDEBAR_MENU_WIDTH:
            return (
                (render_mouse_pos[0] + self.camera.x),
                (render_mouse_pos[1] + self.camera.y),
            )
        
        return None
        
    def current_mouse_indexes(self) -> tuple[int, int] | None:
        
        screen_pos = self.screen_mouse_pos()
        
        if screen_pos is not None:
            return (
                int(screen_pos[0] / TILE_SIZE),
                int(screen_pos[1] / TILE_SIZE)
            )
        
        return None
    
    def manage_button(self) -> None:
        if self.floor_up.is_clicked():
            self.current_floor += 1
            
        if self.floor_down.is_clicked():
            self.current_floor -= 1
    
    
    def draw_grid(self) -> None:
        number_tile_x: int = int(self.render_screen_width / TILE_SIZE) + 1
        number_tile_y: int = int(self.render_screen_height / TILE_SIZE) + 1
        start_pos_x: int = TILE_SIZE - self.camera.x % TILE_SIZE
        start_pos_y: int = TILE_SIZE - self.camera.y % TILE_SIZE
        for i in range(number_tile_x):
            main_line = -1 <= (i * TILE_SIZE + self.camera.x) / TILE_SIZE < 0
            pygame.draw.line(
                self.window,
                (200, 200, 100) if main_line else (200, 200, 200),
                start_pos=self.convert_game_pos((start_pos_x + i * TILE_SIZE, 0)),
                end_pos=self.convert_game_pos((start_pos_x + i * TILE_SIZE, self.screen_height)),
                width=3 if main_line else 1
            )
            
        for i in range(number_tile_y):
            # print(i, (i * TILE_SIZE + self.camera.y) / TILE_SIZE)
            main_line = -1 <= (i * TILE_SIZE + self.camera.y) / TILE_SIZE < 0
            pygame.draw.line(
                self.window,
                (200, 200, 100) if main_line else (200, 200, 200),
                start_pos=self.convert_game_pos((0, start_pos_y + i * TILE_SIZE)),
                end_pos=self.convert_game_pos((self.render_screen_width, start_pos_y + i * TILE_SIZE)),
                width=3 if main_line else 1
            )
            
    def draw_sidebar_menu(self) -> None:
        pygame.draw.rect(
            self.window,
            SIDEBAR_BACKGROUND_COLOR,
            (0, 0, LEFT_SIDEBAR_MENU_WIDTH, self.screen_height)
        )
        
        pygame.draw.rect(
            self.window,
            SIDEBAR_BACKGROUND_COLOR,
            (self.screen_width - RIGTH_SIDEBAR_MENU_WIDTH, 0, RIGTH_SIDEBAR_MENU_WIDTH, self.screen_height)
        )
        
        self.draw_buttons()
        
        # Draw current layout
        for widget in self.menu_layout.get(self.menu_control.selected_values[0], []):
            widget.draw()
            
        if self.json_editor is not None:
            self.json_editor.draw()
        
    def draw_debug_menu(self) -> None:
        debug_dict: dict[str, str] = {
            "Floor": self.current_floor,
            "Current index": self.current_mouse_indexes(),
            "Current position": self.screen_mouse_pos(),
        }
        
        if self.current_mode == "room":
           debug_dict["Selected Room Floor"] = self.selected_room_floor
           debug_dict["Selected Room Wall"] = self.selected_room_wall
           debug_dict["Room Width"] = self.room_width
           debug_dict["Room Height"] = self.room_height
           debug_dict["Placing Room"] = self.is_placing_room
           debug_dict["Selected Room Id"] = self.selected_room_id
           
        elif self.current_mode == "furniture":
            debug_dict["Selected Furniture Asset"] = self.selected_furniture_asset
            debug_dict["Is Placing Furniture"] = self.is_placing_furniture
            if self.selected_furniture:
                debug_dict = debug_dict | {"Selected Furniture " + k: v for k, v in self.selected_furniture.items()}
                
        elif self.current_mode == "door":
            debug_dict["Selected Door Asset"] = self.selected_door_asset
            debug_dict["Is placing door"] = self.is_placing_door
            if self.selected_door:
                debug_dict = debug_dict | {"Selected Door " + k: v for k, v in self.selected_door.items()}
        
        top_draw: int = 0
        for label, value in debug_dict.items():
            surf = self.fonts["debug"].render(f"{label}: {value}", True, "white")
            rect = surf.get_rect(topright=(self.screen_width - RIGTH_SIDEBAR_MENU_WIDTH - 10, top_draw))
            top_draw += surf.get_height() + 5
            self.window.blit(surf, rect)
            
    def draw_buttons(self) -> None:
        buttons: list[Button] = [
            self.save_button,
            self.floor_up,
             self.floor_down
        ]
        
        for button in buttons:
            button.draw()
    
    def draw(self) -> None:
        self.draw_grid()
        self.draw_debug_menu()
        self.draw_rooms()
        self.draw_furnitures()
        self.draw_doors()
        self.draw_sidebar_menu()
        
        self.menu_control.draw()
        
    
    def draw_furnitures(self) -> None:
        
        all_furnitures: list[dict] = get_from_dict(self.level_data, ["furnitures", str(self.current_floor)], [])[:]
        is_placing_furniture: bool = self.current_mode == "furniture" and self.is_placing_furniture and self.selected_furniture
        
        if is_placing_furniture:
            all_furnitures.append(self.selected_furniture)
            
        for i, furniture in enumerate(all_furnitures):
            
            preview_surf: pygame.Surface = pygame.transform.rotate(
                get_from_dict(self.assets, furniture["asset"].split(os.path.sep), None),
                furniture["rotation"] * 90
            )
            
            preview_surf.set_colorkey("white")
            
            
            if is_placing_furniture and i == (len(all_furnitures) - 1):
                preview_surf.set_alpha(180)
            
            self.window.blit(
                preview_surf,
                self.convert_game_pos(
                    self.camera.convert_pos((
                        furniture["indexes"][0] * TILE_SIZE,
                        furniture["indexes"][1] * TILE_SIZE
                    ))
                )
            )
            
    def draw_doors(self) -> None:
        pass
        
    def draw_rooms(self) -> None:
        
        # Rooms
        for room_id, room_obj in get_from_dict(self.level_data, ["rooms", str(self.current_floor)], {}).items():
            indexes: tuple[int, int] = room_obj["indexes"]
            start_x, start_y = indexes
            end_x, end_y = start_x + room_obj["width"], start_y + room_obj["height"]
            
            for i in range(start_x, end_x):
                for j in range(start_y, end_y):
                    is_wall = (i in [start_x, end_x - 1]) or j in [start_y, end_y - 1]
                    
                    selected_tile_path = room_obj["wall_tile" if is_wall else "floor_tile"]
                    
                    if not is_wall:
                        tile_number = int((i + j) % 2)
                        selected_tile_path = os.path.join(selected_tile_path, str(tile_number))
  
                    surf: pygame.Surface = get_from_dict(self.assets, selected_tile_path.split(os.path.sep))
                    
                    self.window.blit(
                        surf,
                        self.convert_game_pos(
                            self.camera.convert_pos((i * TILE_SIZE, j * TILE_SIZE))
                        )
                    )
            
            # Only the selected_room is highlighted      
            if self.current_mode == "room" and self.selected_room_id is not None and self.selected_room_id != room_id:
                dark_highlight_surf = pygame.Surface((room_obj["width"] * TILE_SIZE, room_obj["height"] * TILE_SIZE))
                dark_highlight_surf.set_alpha(100)
                
                self.window.blit(
                    dark_highlight_surf,
                    self.convert_game_pos(
                        self.camera.convert_pos((start_x * TILE_SIZE, start_y * TILE_SIZE))
                    )
                )
                
                    
        # Draw room preview when placing it
        if self.current_mode == "room":
            mouse_index = self.current_mouse_indexes()
            if self.is_placing_room and mouse_index is not None:
                
                topleft = self.convert_game_pos(
                    self.camera.convert_pos((mouse_index[0] * TILE_SIZE, mouse_index[1] * TILE_SIZE))
                )

                pygame.draw.rect(
                    self.window,
                    "green" if self.valid_room_placement else "red",
                    (
                        *topleft,
                        TILE_SIZE * self.room_width,
                        TILE_SIZE * self.room_height
                    ),
                    5
                )
        
    def manage_menu(self, all_events: list[pygame.Event]) -> None:
        if self.current_mode == "room":
            self.manage_room_menu(all_events)
        elif self.current_mode == "furniture":
            self.manage_furniture_menu(all_events)
        elif self.current_mode == "door":
            self.manage_door_menu(all_events)
            
        if self.json_editor is not None:
            self.json_editor.update(all_events)
            
    def manage_room_menu(self, all_events: list[pygame.Event]) -> None:
        
        key_pressed = pygame.key.get_pressed()
        left_clicked: bool = False
        right_clicked: bool = False
        mouse_pressed = pygame.mouse.get_pressed()
                    
        ctrl_pressed = key_pressed[pygame.K_LCTRL]
        
        mouse_indexes = self.current_mouse_indexes()
        
        self.check_valid_room_placement()
        
        for event in all_events:
            if event.type == pygame.MOUSEWHEEL:
                attr_name: str = "room_width" if ctrl_pressed else "room_height"
                setattr(
                    self,
                    attr_name,
                    max(3, getattr(self, attr_name, 0) + event.y)
                )
                
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[0]:
                left_clicked = True
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[2]:
                right_clicked = True

        # Asset selection (wall / floor)    
        for selectable_asset in (w for w in self.menu_layout["room"] if isinstance(w, SelectableAsset)):
            if selectable_asset.is_clicked() or (self.selected_room_wall is None or self.selected_room_floor is None):
                if selectable_asset.key.startswith("Walls"):
                    self.selected_room_wall = selectable_asset.key
                else:
                    self.selected_room_floor = os.path.sep.join(selectable_asset.key.split(os.path.sep)[:-1])
        
                if self.selected_room_id is not None:
                    room_obj: dict = get_from_dict(
                        self.level_data,
                        [   
                            "rooms",
                            str(self.current_floor),
                            self.selected_room_id   
                        ],
                        {}
                    )
                    
                    room_obj["wall_tile"] = self.selected_room_wall
                    room_obj["floor_tile"] = self.selected_room_floor
        
        # Create room
        if Button.all_widgets["create_room"].is_clicked():
            self.is_placing_room = True
            self.selected_room_id = None
            
        # Delete room
        if Button.all_widgets["delete_room"].is_clicked() and self.selected_room_id is not None:
            self.delete_room(self.selected_room_id)
            self.selected_room_id = None
            self.is_placing_room = False

        # Cancel placing room
        if right_clicked and self.is_placing_room:
            self.is_placing_room = False

        # Room placed
        is_room_placed: bool = False
        if left_clicked and mouse_indexes is not None and self.is_placing_room and self.valid_room_placement:
            # print(self.level_data)
            
            room_id = generate_unique_id(
                sum(
                    (list(obj) for obj in self.level_data.get("rooms", {}).values()),
                    start=[]
                )
            )
            
            set_to_dict(
                self.level_data,
                [   
                    "rooms",
                    str(self.current_floor),
                    room_id   
                ],
                {
                    "indexes": mouse_indexes,
                    "wall_tile": self.selected_room_wall,
                    "floor_tile": self.selected_room_floor,
                    "floor": self.current_floor,
                    "width": self.room_width,
                    "height": self.room_height,
                }
            )
            
            # print(self.level_data)
            
            self.selected_room_id = room_id
            
            self.is_placing_room = False
            is_room_placed = True
            
        # Room selection
        if left_clicked and mouse_indexes is not None and not is_room_placed and not self.is_placing_room:
            for id_, room_obj in get_from_dict(self.level_data, ["rooms",str(self.current_floor)], {}).items():
                indexes: tuple[int, int] = room_obj["indexes"]
                start_x, start_y = indexes
                end_x, end_y = start_x + room_obj["width"], start_y + room_obj["height"]
                
                if (start_x < mouse_indexes[0] < end_x - 1) and (start_y <= mouse_indexes[1] < end_y - 1):
                    self.selected_room_id = id_
                    self.selected_room_floor = room_obj["floor_tile"]
                    self.selected_room_wall = room_obj["wall_tile"]
                    self.room_width = room_obj["width"]
                    self.room_height = room_obj["height"]
                    break
            else:
                self.selected_room_id = None
                
    def check_valid_room_placement(self) -> None:
        
        self.valid_room_placement = True
        
        mouse_indexes = self.current_mouse_indexes()
        
        if not self.is_placing_room or mouse_indexes is None:
            self.valid_room_placement = False
            return
        
        current_rect = pygame.Rect(*mouse_indexes, self.room_width, self.room_height)
        
        for room_obj in get_from_dict(self.level_data, ["rooms",str(self.current_floor)], {}).values():
            indexes: tuple[int, int] = room_obj["indexes"]
            start_x, start_y = indexes
            room_rect = pygame.Rect(start_x + 1, start_y + 1, room_obj["width"] - 2, room_obj["height"] - 2)
            if current_rect.colliderect(room_rect):
                self.valid_room_placement = False
                return
                   
    def delete_room(self, room_id: str) -> None:
        for rooms in self.level_data["rooms"].values():
            if room_id in rooms:
                # TODO: Delete associated elements (doors, furnitures, npcs, npc paths)
                del rooms[room_id]
                
    
    def manage_furniture_menu(self, all_events: list[pygame.Event]) -> None:
        key_pressed = pygame.key.get_pressed()
        left_clicked: bool = False
        right_clicked: bool = False
        scroll_y: int = 0
        mouse_pressed = pygame.mouse.get_pressed()
                    
        ctrl_pressed = key_pressed[pygame.K_LCTRL]
        
        mouse_indexes = self.current_mouse_indexes()
        screen_mouse_pos = self.screen_mouse_pos()
        
        for event in all_events:
            if event.type == pygame.MOUSEWHEEL:
                attr_name: str = "room_width" if ctrl_pressed else "room_height"
                setattr(
                    self,
                    attr_name,
                    max(3, getattr(self, attr_name, 0) + event.y)
                )
                
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[0]:
                left_clicked = True
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[2]:
                right_clicked = True
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = event.y
                
        # Asset selection    
        for selectable_asset in (w for w in self.menu_layout["furniture"] if isinstance(w, SelectableAsset)):
            if selectable_asset.is_clicked() or (self.selected_furniture_asset is None):
                self.selected_furniture_asset = selectable_asset.key
                
                self.selected_furniture = {
                    "indexes": (0, 0),
                    "asset": self.selected_furniture_asset,
                    "rotation": 0
                }
                
                self.is_placing_furniture = True

        # Create an new furniture
        # if Button.all_widgets["create_furniture"].is_clicked():
        #     self.selected_furniture = {
        #         "indexes": (0, 0),
        #         "asset": self.selected_furniture_asset,
        #         "rotation": 0
        #     }
        #     self.is_placing_furniture = True
            
        has_selected_furniture: bool = False
        # Furniture selection
        if left_clicked and not self.is_placing_furniture and screen_mouse_pos is not None:
            all_furnitures: list[dict] = get_from_dict(self.level_data, ["furnitures", str(self.current_floor)], [])
            for furniture in all_furnitures:
                surf: pygame.Surface = pygame.transform.rotate(
                        get_from_dict(
                        self.assets, 
                        furniture["asset"].split(os.path.sep), 
                        pygame.Surface((TILE_SIZE, TILE_SIZE))
                    ),
                    furniture["rotation"] * 90
                )

                rect = surf.get_rect(topleft=(furniture["indexes"][0] * TILE_SIZE, furniture["indexes"][1] * TILE_SIZE))
                # print(rect, screen_mouse_pos, rect.collidepoint(screen_mouse_pos))
                if rect.collidepoint(screen_mouse_pos):
                    all_furnitures.remove(furniture)
                    self.selected_furniture = furniture
                    self.selected_furniture_asset = furniture["asset"]
                    self.is_placing_furniture = True
                    has_selected_furniture = True
                    break
                
        
        # Controls whil placing a furniture 
        if self.is_placing_furniture and self.selected_furniture is not None:
            if scroll_y:
                self.selected_furniture["rotation"] = (self.selected_furniture["rotation"] - scroll_y) % 4
                
            if mouse_indexes is not None:
                self.selected_furniture["indexes"] = mouse_indexes
                
            self.selected_furniture["asset"] = self.selected_furniture_asset
            
            if not has_selected_furniture and left_clicked and mouse_indexes is not None:
                # TODO: Check valid postition
                if get_from_dict(
                    self.level_data,
                    ["furnitures", str(self.current_floor)],
                    None
                ) is None:
                    set_to_dict(
                        self.level_data,
                        ["furnitures", str(self.current_floor)],
                        []
                    )
                    
                get_from_dict(
                    self.level_data,
                    ["furnitures", str(self.current_floor)],
                    []
                ).append(self.selected_furniture)
                
                self.selected_furniture = None
                self.is_placing_furniture = False

            if right_clicked:
                self.selected_furniture = None
                self.is_placing_furniture = False
                
    def manage_door_menu(self, all_events: list[pygame.Event]) -> None:
        key_pressed = pygame.key.get_pressed()
        left_clicked: bool = False
        right_clicked: bool = False
        scroll_y: int = 0
        mouse_pressed = pygame.mouse.get_pressed()
                    
        ctrl_pressed = key_pressed[pygame.K_LCTRL]
        
        mouse_indexes = self.current_mouse_indexes()
        screen_mouse_pos = self.screen_mouse_pos()
        
        for event in all_events:
            if event.type == pygame.MOUSEWHEEL:
                attr_name: str = "room_width" if ctrl_pressed else "room_height"
                setattr(
                    self,
                    attr_name,
                    max(3, getattr(self, attr_name, 0) + event.y)
                )
                
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[0]:
                left_clicked = True
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pressed[2]:
                right_clicked = True
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = event.y
                
        
        
    
    def run(self) -> None:
        
        while self.run_loop:
            
            all_events: list[pygame.Event] = pygame.event.get()
            
            key_pressed = pygame.key.get_pressed()
            
            for event in all_events:
                if event.type == pygame.QUIT or ((event.type == pygame.KEYDOWN) and (event.key == pygame.K_ESCAPE)):
                    self.run_loop = False
            
            # Camera controls
            if TextField.active_field() is None:
                camera_speed: int = 6 if key_pressed[pygame.K_LSHIFT] else 3
                if key_pressed[pygame.K_q]:
                    self.camera.x += -camera_speed
                elif key_pressed[pygame.K_d]:
                    self.camera.x += camera_speed
                    
                if key_pressed[pygame.K_z]:
                    self.camera.y += -camera_speed
                elif key_pressed[pygame.K_s]:
                    self.camera.y += camera_speed
                
            self.menu_control.update()
            self.manage_button()
            self.manage_menu(all_events)
                    
            # Draw logic
            self.window.fill(BACKGROUND_COLOR)
            
            self.draw()
            
            
            pygame.display.update()
            self.clock.tick(FPS)
                    
        pygame.quit()
        
    @property
    def screen_size(self) -> tuple[int, int]:
        return self.window.get_size()
        
    @property
    def screen_width(self) -> int:
        return self.screen_size[0]
    
    @property
    def screen_height(self) -> int:
        return self.screen_size[1]
    
    @property
    def render_screen_width(self) -> int:
        return self.screen_width - (LEFT_SIDEBAR_MENU_WIDTH + RIGTH_SIDEBAR_MENU_WIDTH)
        
    @property
    def render_screen_height(self) -> int:
        return self.screen_height
    
    @property
    def current_mode(self) -> str:
        return self.menu_control.selected_values[0]