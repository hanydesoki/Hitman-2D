# import random
import math
import random
from typing import TypedDict, TYPE_CHECKING, Generator, NotRequired

import pygame
from pathfinding.finder.a_star import AStarFinder, DiagonalMovement
from pathfinding.core.grid import Grid, GridNode

from .transition_value import TransitionValue, TransitionRotation
from .utilities import find_all_paths
from .geometry import segments_intersect
from .settings import TILE_SIZE


if TYPE_CHECKING: # Always false: Avoid circular loop so we can use it as type hinting
    from .game import Game
    from .weapon import Weapon
    from .game import Room
    from .door import Door
    from .food import Food

from .settings import NPCPathData, NPCActionType
    
class DisguiseData(TypedDict):
    name: str
    arm: pygame.Surface
    legs: pygame.Surface
    shoulder: pygame.Surface
    torso: pygame.Surface


class CharacterData(TypedDict):
    name: str
    face: pygame.Surface
    top_head: pygame.Surface
    
    
class FocusPosition(TypedDict):
    x: TransitionValue
    y: TransitionValue
    rotation: TransitionRotation
    
    
class AvailableActions(TypedDict):
    pass_door: NotRequired[Door]
    fiber_wire_npc: NotRequired[NPC]
    knock_out_npc: NotRequired[NPC]
    sedate_npc: NotRequired[NPC]
    lethal_poison_food: NotRequired[Food]
    emetic_poison_food: NotRequired[Food]
    sedate_poison_food: NotRequired[Food]
    drag_body: NotRequired[NPC]
    release_body: NotRequired[NPC]
    swap_disguise: NotRequired[NPC]
    
    
class GameCharacter:
    
    drag_speed: float = 0.6
    walk_speed: float = 1.0
    run_speed: float = 2.0
    
    def __init__(
        self,
        game: "Game",
        x: float,
        y: float,
        rotation: int,
        disguise: DisguiseData,
        character: CharacterData,
        room_id: str,
        floor_id: str,
        is_target: bool = False,
        paths: list[NPCPathData] = None,
        
        weapon: "Weapon" | None = None
    ):  
        self.game = game
        self.x = x
        self.y = y
        self.rotation = rotation
        self.disguise = disguise
        self.character = character
        self.room_id = room_id
        self.floor_id = floor_id
        self.is_target = is_target
        self.original_path: list[NPCPathData] = paths or []
        self.paths: list[NPCPathData] = self.original_path[:]
        self.weapon = weapon
        
        self.door_transition: bool = False
        
        self.rect = self.character["top_head"].get_rect(center=(x, y))
        
        self.inconsious_surf: pygame.Surface = None
        self.udpate_inconsious_surf()
        
        self.inconsious: bool = False
        self.alive: bool = True
        self.sleeping: bool = False
        
        self.wait_time: int = 0
        self.is_waiting: bool = False
        self.finished_current_path: bool = False
        
        self.vx: float = 0
        self.vy: float = 0
        
        self.busy_frame: int = 0
        self.max_busy_frame: int = 0
        
        self.focus_points: list[FocusPosition] = []
        self.current_pathfinding: list[pygame.Rect] = []
        self.room_to_traverse: list[str] = []
        self.target_room_position: tuple[float, float] = None
        
        self.next_door: Door | None = None
        
        self.locked: bool = False
        
        self.dragged_body: "GameCharacter" | None = None
        
        self.metadata: dict = {}
        
        self._line_of_sight_points_debug: list[tuple[float, float, bool]] = []
    
    def udpate_inconsious_surf(self) -> None:
        surf_head = self.character["face"].copy()
        surf_torso = self.disguise["torso"].copy()
        surf_legs = self.disguise["legs"].copy()
        
        self.inconsious_surf = pygame.Surface((
            max(surf_head.get_width(), surf_torso.get_width(), surf_legs.get_width()),
            surf_head.get_height() + surf_torso.get_height() + surf_legs.get_height()
        ))
        
        self.inconsious_surf.fill("black")
        
        top = 0
        for surf in [surf_head, surf_torso, surf_legs]:
            self.inconsious_surf.blit(
                surf, 
                (int(self.inconsious_surf.get_width() / 2 - surf.get_width() / 2), top)
            )
            top += surf.get_height()        
    
    def focus_position(self, 
        target_position: tuple[float, float], 
        target_rotation: float, 
        number_frames: int, 
        clear_queue: bool = False
    ) -> None:
        
        if clear_queue:
            self.focus_points.clear()
            
        if self.focus_points:
            start_x = self.focus_points[-1]["x"].end
            start_y = self.focus_points[-1]["y"].end
            start_rotation = self.focus_points[-1]["rotation"].end
        else:
            start_x = self.x
            start_y = self.y
            start_rotation = self.rotation
        
        self.focus_points.append({
            "x": TransitionValue(start_x, target_position[0], number_frames),
            "y": TransitionValue(start_y, target_position[1], number_frames), 
            "rotation": TransitionRotation(start_rotation, target_rotation, number_frames)
        })

    def draw(self) -> None:
        if not self.inconsious:
            top_head_surf = pygame.transform.rotate(self.character["top_head"], self.rotation)
            top_head_surf.set_colorkey("black")
            top_head_rect = top_head_surf.get_rect(center=self.rect.center)
            
            shoulder_surf = pygame.transform.rotate(self.disguise["shoulder"], self.rotation)
            shoulder_surf.set_colorkey("black")
            shoulder_rect = shoulder_surf.get_rect(center=self.rect.center)
            
            self.game.window.blit(shoulder_surf, self.game.camera.convert_pos(shoulder_rect.topleft))
            self.game.window.blit(top_head_surf, self.game.camera.convert_pos(top_head_rect.topleft))
            
            # collision_rect = self.rect.copy()
            # collision_rect.topleft = self.game.camera.convert_pos(top_head_rect.topleft)
            # pygame.draw.rect(self.game.window, "green", collision_rect, width=1)
        else:
            rotated_surf = pygame.transform.rotozoom(self.inconsious_surf, (self.rotation + 180) % 360, 0.7)
            rotated_surf.set_colorkey("black")
            
            self.game.window.blit(
                rotated_surf,
                self.game.camera.convert_pos((int(self.x - rotated_surf.get_width() / 2), int(self.y - rotated_surf.get_height() / 2)))
            )
        
    def manage_movement(self) -> None:
        
        if self.locked: return
        
        if self.manage_focus_transitions(): return
        
        self.x += self.vx
        self.rect.centerx = self.x
        
        rect = self.check_collision()

        if rect is not None:
            if self.vx > 0:
                self.rect.right = rect.left
                self.x = self.rect.centerx
            elif self.vx < 0:
                self.rect.left = rect.right
                self.x = self.rect.centerx
                
        
        self.y += self.vy
        self.rect.centery = self.y
        
        rect = self.check_collision()
        
        if rect is not None:
            if self.vy > 0:
                self.rect.bottom = rect.top
                self.y = self.rect.centery
            elif self.vy < 0:
                self.rect.top = rect.bottom
                self.y = self.rect.centery
                
        
        
    def check_collision(self) -> pygame.Rect | None:
        for collision_rect in self.get_room_collision_rects():
            if self.rect.colliderect(collision_rect):
                return collision_rect
        
        return None
    
    def manage_focus_transitions(self) -> bool:
        
        if not self.focus_points: return False
        
        self.vx = 0
        self.vy = 0
        
        current_focus = self.focus_points[0]
        
        current_focus_done: bool = True
        
        current_focus["x"].udpate()
        self.x = current_focus["x"].value
        self.rect.centerx = self.x
        current_focus_done = current_focus_done and current_focus["x"].done
        
        current_focus["y"].udpate()
        self.y = current_focus["y"].value
        self.rect.centery = self.y
        current_focus_done = current_focus_done and current_focus["y"].done
        
        current_focus["rotation"].udpate()
        self.rotation = current_focus["rotation"].value
        current_focus_done = current_focus_done and current_focus["rotation"].done
        
        if current_focus_done:
            self.focus_points.pop(0)
        
        return True
        
    def pass_door(self, door: Door) -> None:
        
        self.vx = 0
        self.vy = 0
        
        current_room_trigger = door.trigger_rects[self.room_id]
        target_room_id = [rid for rid in door.trigger_rects.keys() if rid != self.room_id][0]
        target_room_trigger = door.trigger_rects[target_room_id]
        
        is_vertical: bool = door.rotation in [1, 3]
        
        if is_vertical:
            rotation = (door.rotation * 90 + (
                current_room_trigger.x < target_room_trigger.x
            ) * 180) % 360
        else:
            rotation = (door.rotation * 90 + (
                current_room_trigger.y < target_room_trigger.y
            ) * 180) % 360
        
        door.open_door()
        self.focus_position(
            target_position=current_room_trigger.center,
            target_rotation=rotation,
            number_frames=30,
            clear_queue=True
        )
        
        self.focus_position(
            target_position=target_room_trigger.center,
            target_rotation=rotation,
            number_frames=60
        )
        
        self.room_id = target_room_id
        
        self.current_pathfinding.clear()
        self.next_door = None
        
        
    def update(self) -> None:
        pass
        
    def get_room_collision_rects(self) -> Generator[pygame.Rect, None, None]:
        for wall_rect in self.current_room["walls"]:
            yield wall_rect
            
        for _, __, furniture_rect in self.current_room["furnitures"]:
            yield furniture_rect
            
    def go_to(self, position: tuple[int, int]) -> None:
        
        target_room: str = None
        
        for room_id, room in self.game.level_rooms[self.floor_id].items():
            if room["rect"].collidepoint(position):
                target_room = room_id
                break
        
        if target_room is None: return
        
        self.current_pathfinding.clear()
        
        self.room_to_traverse = [self.room_id]
        
        if self.room_id != target_room:
            self.room_to_traverse = find_all_paths(self.game.room_graph_links[self.floor_id], self.room_id, target_room)[0]
        
        self.target_room_position = position
        # print(self.room_to_traverse)
        
    def drag_body(self, other: "GameCharacter") -> None:
        if other.inconsious:
            
            def drag_npc() -> None:
                self.dragged_body = other
                
            self.game.scheduler.add(drag_npc, 30)
            self.focus_position(
                target_position=other.rect.center,
                target_rotation=(self.rotation + 20) % 360,
                number_frames=30
            )
            self.busy_frame = 30
            self.max_busy_frame = 30
            
    def release_body(self) -> None:
        self.dragged_body = None
        
    def manage_npc_behaviour(self) -> None:
        
        if self.locked: return
        
        if self.inconsious: return
        
        if not self.paths and self.original_path:
            self.paths.extend(self.original_path)
            # print("loop_back")
        
        if not self.paths: return
        
        if not self.is_waiting and self.paths and not self.current_pathfinding:
            self.go_to(position=self.paths[0]["position"])
            
        # Manage waiting
        if self.is_waiting:
            self.wait_time += 1
            if self.wait_time >= self.paths[0]["time"]:
                self.paths.pop(0)
                # print("finish waiting", self.wait_time, self.paths)
                self.wait_time = 0
                self.is_waiting = False
                
        # Eat food
        if self.current_pathfinding and self.paths and (self.paths[0]["action_type"] == NPCActionType.food_interaction):
            
            food: Food = self.paths[0].get("metadata", {}).get("food", None)

            if food is not None and food.trigger_rect.collidepoint((self.x, self.y)):
                if (food.trigger_rect.x != food.rect.x):
                    rotation = -90 if (food.trigger_rect.x < food.rect.x) else 90
                else:
                    rotation = 180 if (food.trigger_rect.y < food.rect.y) else -180   
                    
                self.focus_position(food.trigger_rect.center, rotation, 30)
                self.eat(food)
                
                self.current_pathfinding.clear()
                self.room_to_traverse.clear()
                self.target_room_position = None
                self.is_waiting = True
                    
                
        self.finished_current_path = False
            
    def manage_pathfinding(self) -> None:
        
        if self.locked: return
        
        if self.inconsious: return
        
        # Follow the train CJ
        if self.current_pathfinding:
            
            next_node_rect = self.current_pathfinding[0]
            
            dx = next_node_rect.centerx - self.x
            dy = next_node_rect.centery - self.y
            
            norm: float = math.sqrt(dx ** 2 + dy ** 2)
            
            speed = self.walk_speed
            if self.dragged_body is not None:
                speed = self.drag_speed
            
            self.vx = dx / norm * speed
            self.vy = dy / norm * speed
            
            self.rotation = math.degrees(math.atan2(-dy, dx) - math.pi / 2)
            # print(self.rotation)
            
            if next_node_rect.collidepoint(self.x, self.y):
                self.current_pathfinding.pop(0)
            
            # Finished path
            if len(self.room_to_traverse) == 1 and not self.current_pathfinding:
                self.room_to_traverse.clear()
                self.current_pathfinding.clear()
                self.next_door = None
                self.target_room_position = None
                self.is_waiting = True
                self.vx = 0
                self.vy = 0
 
        if self.next_door is not None and self.next_door.trigger_rects[self.room_id].collidepoint(self.x, self.y):
            self.room_to_traverse.pop(0)
            self.pass_door(self.next_door)
            
        # Create pathfinding between npc and next door or end 
        if not self.current_pathfinding and self.room_to_traverse and not self.focus_points:
            if len(self.room_to_traverse) > 1:
                next_room_id = self.room_to_traverse[1]
                for door in self.current_room["doors"]:
                    if next_room_id in door.trigger_rects:
                        self.next_door = door
                        break
                    
                self.create_pathfinding(
                    from_position=(self.x, self.y),
                    to_position=self.next_door.trigger_rects[self.room_id].center
                )
            elif len(self.room_to_traverse) == 1:
                self.create_pathfinding(
                    from_position=(self.x, self.y),
                    to_position=self.target_room_position
                )
                
    def eat(self, food: Food) -> None:
        pass
            
    def create_pathfinding(self, from_position: tuple[float, float], to_position: tuple[float, float]) -> None:
        
        start: tuple[int, int] = (
            int(from_position[0] / TILE_SIZE) - self.current_room["indexes"][0],
            int(from_position[1] / TILE_SIZE) - self.current_room["indexes"][1],
        )
        
        end: tuple[int, int] = (
            int(to_position[0] / TILE_SIZE) - self.current_room["indexes"][0],
            int(to_position[1] / TILE_SIZE) - self.current_room["indexes"][1],
        )
        
        # Check if in bound and accessible
        if (
            (
                not (0 <= start[0] < self.current_room["width"])
                or
                not (0 <= start[1] < self.current_room["height"])
                or
                not (0 <= end[0] < self.current_room["width"])
                or
                not (0 <= end[1] < self.current_room["height"])
            )
            and
            (
                self.current_room["pathfinding_grid"][start[0]][start[1]] == 0
                or
                self.current_room["pathfinding_grid"][end[0]][end[1]] == 0
            ) 
            
        ):
            return
        
        a_start_finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)   
        grid = Grid(matrix=self.current_room["pathfinding_grid"])
        
        pathfinding_list, _ = a_start_finder.find_path(grid.node(*start), grid.node(*end), grid)
        pathfinding_list: list[GridNode]
        
        
        self.current_pathfinding.clear()
        
        node_size: int = int(TILE_SIZE / 5)
        
        for grid_node in pathfinding_list:
            node_position: tuple[float, float] = (
                (grid_node.x + self.current_room["indexes"][0]) * TILE_SIZE + TILE_SIZE / 2,
                (grid_node.y + self.current_room["indexes"][1]) * TILE_SIZE + TILE_SIZE / 2,
            )
            
            node_rect = pygame.Rect(
                node_position[0] - node_size / 2,
                node_position[1] - node_size / 2,
                node_size,
                node_size
            )
            
            self.current_pathfinding.append(node_rect)
            
        # print(self.current_pathfinding)
        
    def swap_disguise(self, other: "GameCharacter") -> None:
        # print("swap")
        
        def switch_npc_disguise() -> None:
            other.disguise, self.disguise = self.disguise, other.disguise
            
            other.udpate_inconsious_surf()
            self.udpate_inconsious_surf()
            
        self.game.scheduler.add(switch_npc_disguise, 60 * 3)
        self.max_busy_frame = 60 * 3
        self.busy_frame = 60 * 3
        self.focus_position(
            target_position=other.rect.center, 
            target_rotation=(other.rotation + 180) % 360, 
            number_frames=30
        )
        
    def can_see_point(self, point: tuple[float, float], player_see_through: bool = False, body_see_through: bool = False) -> bool:
        # Check if inside the same room
        if not self.current_room["rect"].collidepoint(point): return
        
        # TODO: Check character orientation
        dx = self.x - point[0]
        dy = self.y - point[1]
        
        squared_dist = dx ** 2 + dy ** 2
        
        if squared_dist == 0: return True
        
        npc_radian_angle = math.radians((self.rotation + 90) % 360)
        fx = math.cos(npc_radian_angle)
        fy = math.sin(npc_radian_angle)

        dist = math.sqrt(squared_dist)

        dir_x = dx / dist
        dir_y = -dy / dist

        dot_product = fx * dir_x + fy * dir_y

        if dot_product > 0: return False
        
        # Check all furniture intersection
        for furniture_data, _, rect in self.current_room["furnitures"]:
            if player_see_through and furniture_data.get("player_see_through", False): continue
            if body_see_through and furniture_data.get("body_see_through", False): continue
            
            if self.segment_intersect_rect(self.x, self.y, point[0], point[1], rect=rect): return False
            
        return True
            
    @staticmethod
    def segment_intersect_rect(x1: float, y1: float, x2: float, y2: float, rect: pygame.Rect) -> bool:
        if segments_intersect(x1, y1, x2, y2, *rect.topleft, *rect.topright): return True
        if segments_intersect(x1, y1, x2, y2, *rect.topright, *rect.bottomright): return True
        if segments_intersect(x1, y1, x2, y2, *rect.bottomright, *rect.bottomleft): return True
        if segments_intersect(x1, y1, x2, y2, *rect.bottomleft, *rect.topleft): return True
        
        return False
        
        
    def manage_body_dragged(self) -> None:
        if self.dragged_body is None: return
        
        self.dragged_body.x, self.dragged_body.y = self.rect.center
        
    def _scan_line_of_sight(self, player_see_through: bool = False, body_see_through: bool = False) -> None:
        start_pos_x = self.current_room["position"][0] + TILE_SIZE
        end_pos_x = self.current_room["position"][0] + self.current_room["pixel_width"] - TILE_SIZE
        
        start_pos_y = self.current_room["position"][1] + TILE_SIZE
        end_pos_y = self.current_room["position"][1] + self.current_room["pixel_height"] - TILE_SIZE
        
        step = 10
        self._line_of_sight_points_debug.clear()
        for x in range(start_pos_x, end_pos_x, 10):
            for y in range(start_pos_y, end_pos_y, 10):
                pos = (x, y)
                self._line_of_sight_points_debug.append((*pos, self.can_see_point(pos, player_see_through, body_see_through)))
        
    @property
    def current_room(self) -> Room:
        return self.game.level_rooms[self.floor_id][self.room_id]
 
 
class NPC(GameCharacter):
    
    def update(self):
        self.manage_npc_behaviour()
        self.manage_pathfinding()
        self.manage_body_dragged()
        self.manage_movement()
        # self.manage_focus_transitions()
        
    def pass_door(self, door) -> None:
        self.current_room["npcs"].remove(self)
        if self.dragged_body is not None:
            self.current_room["npcs"].remove(self.dragged_body)
            
        super().pass_door(door)
        self.current_room["npcs"].append(self)
        
        if self.dragged_body is not None:
            self.current_room["npcs"].append(self.dragged_body)
        
        
        
class Player(GameCharacter):
    
    MAX_NPC_INTERACTION_DISTANCE: float = 40
    MIN_NPC_INTERACTION_DISTANCE: float = 10

    def __init__(self, game, x, y, rotation, disguise, character, room_id, floor_id, is_target = False, paths = None, weapon = None):
        super().__init__(game, x, y, rotation, disguise, character, room_id, floor_id, is_target, paths, weapon)
        
        self.available_actions: AvailableActions = {}
        self.action_menu_index: int = None
        
        
    def manage_available_actions(self) -> None:
        
        current_selected_action: str | None = None        
        if self.available_actions and self.action_menu_index is not None:
            action_list = list(self.available_actions)
            
            current_selected_action = action_list[self.action_menu_index]
        
        self.available_actions.clear()
        
        # Check if player is close to a door
        for door in self.current_room["doors"]:
            if door.trigger_rects[self.room_id].collidepoint((self.x, self.y)):
                self.available_actions["pass_door"] = door
                break
            
        # Check if player is inside a food trigger
        for food in self.current_room["foods"]:
            if food.trigger_rect.collidepoint((self.x, self.y)):
                # TODO: Check player inventory for poisons
                self.available_actions["lethal_poison_food"] = food
                self.available_actions["emetic_poison_food"] = food
                self.available_actions["sedate_poison_food"] = food
                break
        
        
        for npc in self.current_room["npcs"]:
            
            if npc.inconsious:
                if self.dragged_body is None and npc.rect.colliderect(self.rect):
                    self.available_actions["drag_body"] = npc
                    self.available_actions["swap_disguise"] = npc
                elif self.dragged_body is not None:
                    self.available_actions["release_body"] = self.dragged_body      
            else:
                dx = self.x - npc.x 
                dy = self.y - npc.y
                squared_dist = (dx ** 2 + dy ** 2)
                # Check if player is right behind a NPC
                if (
                    squared_dist != 0
                    and (squared_dist <= self.MAX_NPC_INTERACTION_DISTANCE ** 2) # Player is close enough to the npc
                ): 
                    npc_radian_angle = math.radians((npc.rotation + 90) % 360)
                    fx = math.cos(npc_radian_angle)
                    fy = math.sin(npc_radian_angle)
                    
                    dist = math.sqrt(squared_dist)
                    
                    dir_x = dx / dist
                    dir_y = -dy / dist
                    
                    dot_product = fx * dir_x + fy * dir_y
                    
                    if dot_product <= -0.5:
                        self.available_actions["fiber_wire_npc"] = npc
                        self.available_actions["knock_out_npc"] = npc
                        self.available_actions["sedate_npc"] = npc # TODO: Check inventory
                        break
        
        if current_selected_action in self.available_actions:
            self.action_menu_index = list(self.available_actions).index(current_selected_action)
        elif self.action_menu_index is None and self.available_actions:
            self.action_menu_index = 0
        else:
            self.action_menu_index = None
        
    def manage_controls(self, all_events: list[pygame.Event]) -> None:
        
        # if pygame.key.get_just_released()[pygame.K_SPACE]:
        #     self.focus_position(
        #         (random.randint(100, 500), (random.randint(100, 500))),
        #         random.randint(100, 359),
        #         60 * 2,
        #     )
        
        # if pygame.mouse.get_just_released()[0]:
        #     mouse_pos = pygame.mouse.get_pos()
        #     self.go_to(mouse_pos)
        
        if self.busy_frame > 0: return
        
        if self.current_pathfinding: return

        if self.door_transition or self.focus_points: return
        
        key_pressed = pygame.key.get_pressed()
        
        if key_pressed[pygame.K_LEFT]:
            self.rotation = (self.rotation + 6) % 360
        if key_pressed[pygame.K_RIGHT]:
            self.rotation = (self.rotation - 6) % 360
            
        scroll_y: int = 0
        
        for event in all_events:
            if event.type == pygame.MOUSEWHEEL:
                scroll_y = event.y
                
        if scroll_y and self.action_menu_index is not None and self.available_actions:
            self.action_menu_index = (self.action_menu_index - scroll_y) % len(self.available_actions)
        
        speed: float = self.run_speed if key_pressed[pygame.K_LSHIFT] else self.walk_speed
        
        if self.dragged_body is not None:
            speed = self.drag_speed
        
        self.vx = 0
        self.vy = 0
        
        if key_pressed[pygame.K_q]:
            self.vx = -speed
        elif key_pressed[pygame.K_d]:
            self.vx = speed
                    
        if key_pressed[pygame.K_z]:
            self.vy = -speed
        elif key_pressed[pygame.K_s]:
            self.vy = speed            

        if not (self.vx == 0 and self.vy == 0):
            magnitude = math.sqrt(self.vx ** 2 + self.vy ** 2)

            self.vx = self.vx / magnitude * speed
            self.vy = self.vy / magnitude * speed
        
        # Pressing Space will attempt to execute the current selected action in the topleft menu
        if pygame.key.get_just_released()[pygame.K_SPACE]:
            self.execute_selected_action()
            
        # if pygame.key.get_just_released()[pygame.K_l]:
        if key_pressed[pygame.K_l]:
            self._scan_line_of_sight(player_see_through=False, body_see_through=False)
            
        if pygame.key.get_just_released()[pygame.K_c]:
            self._line_of_sight_points_debug.clear()
    
    def execute_selected_action(self) -> None:
        if (not self.available_actions or self.action_menu_index is None): return
        
        current_action_key = list(self.available_actions)[self.action_menu_index]
        # print(current_action_key)
        # Pass throug the door and change room
        if current_action_key == "pass_door":
            door = self.available_actions.get("pass_door", None)
            if door is not None:
                self.pass_door(door)
                return
        
        if current_action_key == "sedate_npc":
            return self.pacify(npc=self.available_actions["sedate_npc"], pacification_type=0, pacification_time=60 * 5)
                
        if current_action_key == "knock_out_npc":
            return self.pacify(npc=self.available_actions["knock_out_npc"], pacification_type=1, pacification_time=60 * 5)
        
        if current_action_key == "fiber_wire_npc":
            return self.pacify(npc=self.available_actions["fiber_wire_npc"], pacification_type=2, pacification_time=60 * 2)
        
        if current_action_key == "swap_disguise":
            return self.swap_disguise(self.available_actions["swap_disguise"])
            
        if current_action_key == "drag_body":
            return self.drag_body(self.available_actions["drag_body"])
        
        if current_action_key == "release_body":
            return self.release_body()
            
    def pacify(self, npc: "NPC", pacification_type: int, pacification_time: int) -> None:
        """Pacify any npc

        Args:
            npc (NPC): NPC to pacify
            pacification_type (int): Type of pacification ->  0: Sedate; 1: Knock out;  2: Kill;
            pacification_time (int): Time it take to pacify the npc
        """
        npc_radian_angle = math.radians((npc.rotation + 90) % 360)
        fx = math.cos(npc_radian_angle)
        fy = -math.sin(npc_radian_angle)
        
        self.focus_position(
            target_position=(npc.x - 15 * fx, npc.y - 15 * fy), 
            target_rotation=npc.rotation, 
            number_frames=20
        )
        npc.locked = True
        npc.vx = 0
        npc.vy = 0
        self.max_busy_frame = pacification_time
        self.busy_frame = self.max_busy_frame
        
        def incousious_npc() -> None:
            npc.inconsious = True
            
            if pacification_type == 0: # Sedate
                npc.sleeping = True
            elif pacification_type == 1: # Knock out
                npc.sleeping == False
            elif pacification_type == 2: # Kill
                self.alive = False 
                
            npc.locked = False
        
        self.game.scheduler.add(task=incousious_npc, schedule=pacification_time)
        
    def update(self, all_events: list[pygame.Event]):
        self.manage_available_actions()
        self.manage_body_dragged()
        self.manage_controls(all_events=all_events)
        self.manage_pathfinding()
        self.manage_busy()
        self.manage_movement()

        
    def manage_busy(self) -> None:
        self.busy_frame = max(0, self.busy_frame - 1)
        
        if self.busy_frame == 0:
            self.max_busy_frame = 0
            
    def pass_door(self, door):
        
        if self.dragged_body is not None:
            self.current_room["npcs"].remove(self.dragged_body)
        super().pass_door(door)
        
        if self.dragged_body is not None:
            self.current_room["npcs"].append(self.dragged_body)
        
            
    def draw(self) -> None:
        super().draw()

        if self.busy_frame:
            rect_width: int = 70
            rect_height: int = 10
            rect_x = self.rect.centerx - rect_width / 2
            pygame.draw.rect(
                self.game.window,
                "lightgray",
                (
                    *self.game.camera.convert_pos((rect_x,
                    self.rect.top - rect_height - 10)),
                    rect_width,
                    rect_height
                )
            )
            
            pygame.draw.rect(
                self.game.window,
                "red",
                (
                    *self.game.camera.convert_pos((rect_x,
                    self.rect.top - rect_height - 10)),
                    int(rect_width * (1 - self.busy_frame / self.max_busy_frame)),
                    rect_height
                )
            )
        
        # Test line of sight mechanic
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_game = self.game.camera.reverse_pos(mouse_pos)
        
        pygame.draw.line(
            self.game.window, 
            "green" if self.can_see_point(mouse_pos_game) else "red",
            start_pos=self.game.camera.convert_pos((self.x, self.y)),
            end_pos=mouse_pos,
        )
        
        for x, y, can_see in self._line_of_sight_points_debug:
            pygame.draw.circle(
                self.game.window,
                "green" if can_see else "red",
                self.game.camera.convert_pos((x, y)),
                2
            )
            
class Civilian(NPC):
    pass

class Guard(NPC):
    pass
        
        
