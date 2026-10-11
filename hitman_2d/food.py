import pygame

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game

class Food:
    
    poison_colors: dict[str, tuple[int, int, int]] = {
        1: (100, 100, 255), # Sedative
        2: (100, 255, 100), # Emetic
        3: (255, 50, 50), # Lethal
    }
    
    def __init__(self, game: "Game", x: int, y: int, surface: pygame.Surface, trigger_rect: pygame.Rect):
        self.game = game
        self.x = x
        self.y = y
        self.surf = surface
        self.rect = self.surf.get_rect(center=(x, y))
        self.trigger_rect = trigger_rect
        
        self.poison: int = 0
        
    def draw(self) -> None:
        self.game.window.blit(
            self.surf,
            self.game.camera.convert_pos(self.rect.topleft)
        )
        
        # TODO: Draw particles if poisonned
        if self.poisonned:
            pass
    
    @property
    def poisonned(self) -> bool:
        return self.poison != 0