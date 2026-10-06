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
    
    
class NPC:
    
    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        rotation: int,
        disguise: DisguiseData,
        character: CharacterData,
        is_target: bool = False,
        
        weapon: "Weapon" | None = None
    ):  
        self.game = game
        self.x = x
        self.y = y
        self.rotation = rotation
        self.disguise = disguise
        self.character = character
        
        self.is_target = is_target
        
        self.inconsious: bool = False
        self.alive: bool = True
        self.sleeping: bool = False
        
        self.metadata: dict = {}
        
        
class Player(NPC):
    pass

class Civilian(NPC):
    pass

class Guard(NPC):
    pass
        
        
