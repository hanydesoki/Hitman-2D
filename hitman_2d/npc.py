# import random
import math
from typing import TypedDict, TYPE_CHECKING, Generator

import pygame

if TYPE_CHECKING: # Always false: Avoid circular loop so we can use it as type hinting
    from .game import Game
    from .weapon import Weapon
    from .game import Room


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
    
    
class GameCharacter:
    
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
        self.weapon = weapon
        
        self.door_transition: bool = False
        
        self.rect = self.character["top_head"].get_rect(center=(x, y))
        
        self.inconsious: bool = False
        self.alive: bool = True
        self.sleeping: bool = False
        
        self.vx: float = 0
        self.vy: float = 0
        
        self.metadata: dict = {}
        
    def draw(self) -> None:
        if self.alive and not self.inconsious:
            top_head_surf = pygame.transform.rotate(self.character["top_head"], self.rotation)
            top_head_surf.set_colorkey("white")
            top_head_rect = top_head_surf.get_rect(center=self.rect.center)
            
            shoulder_surf = pygame.transform.rotate(self.disguise["shoulder"], self.rotation)
            shoulder_surf.set_colorkey("white")
            shoulder_rect = shoulder_surf.get_rect(center=self.rect.center)
            
            self.game.window.blit(shoulder_surf, self.game.camera.convert_pos(shoulder_rect.topleft))
            self.game.window.blit(top_head_surf, self.game.camera.convert_pos(top_head_rect.topleft))
            
            collision_rect = self.rect.copy()
            collision_rect.topleft = self.game.camera.convert_pos(top_head_rect.topleft)
            pygame.draw.rect(self.game.window, "green", collision_rect, width=1)
        else:
            pass
        
    def manage_movement(self) -> None:
        
        self.x += self.vx
        self.rect.centerx = self.x
        
        rect = self.check_collision()
        

        if rect is not None:
            print(rect.left - 1, self.rect.right)
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
        
    def update(self) -> None:
        pass
        
    def get_room_collision_rects(self) -> Generator[pygame.Rect, None, None]:
        for wall_rect in self.current_room["walls"]:
            yield wall_rect
            
        for _, __, furniture_rect in self.current_room["furnitures"]:
            yield furniture_rect
            
    @property
    def current_room(self) -> Room:
        return self.game.level_rooms[self.floor_id][self.room_id]
 
class NPC(GameCharacter):
    
    def update(self):     
        self.manage_movement()
        
        
class Player(GameCharacter):
    
    def manage_controls(self) -> None:
        if self.door_transition: return
        
        key_pressed = pygame.key.get_pressed()
        
        speed: float = self.walk_speed
        
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

            self.vx /= magnitude
            self.vy /= magnitude
        
    def update(self):
        self.manage_controls()
        self.manage_movement()
        
        

class Civilian(NPC):
    pass

class Guard(NPC):
    pass
        
        
