import random
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
        else:
            pass
        
    def manage_movement(self) -> None:
        self.x += self.vx
        self.rect.x = self.x
        
        rect = self.check_collision()
        if rect is not None:
            if self.vx > 0:
                self.rect.right = rect.left
            else:
                self.rect.left = rect.right
            self.x = self.rect.centerx
        
        self.y += self.vy
        self.rect.y = self.y
        
        rect = self.check_collision()
        
        if rect is not None:
            if self.vy > 0:
                self.rect.bottom = rect.top
            else:
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
        self.rotation = (self.rotation + 1) % 360
        # self.vx = random.random() * 2 - 1
        # self.vy = random.random() * 2 - 1
        
        self.manage_movement()
        
        
class Player(GameCharacter):
    pass

class Civilian(NPC):
    pass

class Guard(NPC):
    pass
        
        
