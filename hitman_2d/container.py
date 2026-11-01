import math
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .game import Game
    from .npc import NPC


class Container:
    
    def __init__(self, game: Game, main_rect: pygame.Rect, trigger_rect: pygame.Rect, capacity: int = 1):
        self.game = game
        self.main_rect = main_rect
        self.trigger_rect = trigger_rect
        self.capacity = capacity
        
        self.bodies: list[NPC] = []
        
        dx = self.trigger_rect.centerx - self.main_rect.centerx
        dy = self.trigger_rect.centery - self.main_rect.centery
        
        self.player_rotation = math.degrees(math.atan2(-dy, dx)) + 90
        
    
    @property  
    def full(self) -> bool:
        return len(self.bodies) >= self.capacity
    