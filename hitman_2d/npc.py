from typing import TypedDict, TYPE_CHECKING

import pygame

if TYPE_CHECKING: # Always false: Avoid circular loop so we can use it as type hinting
    from .game import Game
    from .weapon import Weapon


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
        x: int,
        y: int,
        rotation: int,
        disguise: DisguiseData,
        character: CharacterData,
        room_id: str,
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
        self.is_target = is_target
        self.weapon = weapon
        
        self.rect = self.character["top_head"].get_rect(center=(x, y))
        
        self.inconsious: bool = False
        self.alive: bool = True
        self.sleeping: bool = False
        
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
        
    def update(self) -> None:
        pass


 
class NPC(GameCharacter):
    def update(self):
        self.rotation = (self.rotation + 1) % 360
        
        
class Player(GameCharacter):
    pass

class Civilian(NPC):
    pass

class Guard(NPC):
    pass
        
        
