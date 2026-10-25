import random
from typing import TYPE_CHECKING

import pygame


if TYPE_CHECKING:
    from .game import Game

class SmokeParticle:
    
    def __init__(self, game: Game, x: float, y: float, radius: float, duration: int, color: tuple[int, int, int]):
        self.game = game
        
        self.x = x
        self.y = y
        self.radius = radius
        
        self.radius_growth = 0.05
        
        self.duration = duration
        self.frame = 0
        
        self.color = color
        
        self.vx = random.random() * 0.4 - 0.2
        self.vy = -0.2 - random.random() * 0.4
        
        self.surf: pygame.Surface = None
        self.rect: pygame.Rect = None
        
    def draw(self) -> None:
        if self.surf is not None and self.rect is not None: 
            self.game.window.blit(self.surf, self.game.camera.convert_pos(self.rect.topleft))
        
    @property
    def active(self) -> bool:
        return self.frame < self.duration
        
    def update(self) -> None:
        
        if self.frame >= self.duration: return
        
        self.surf = pygame.Surface((2 * self.radius, 2 * self.radius))
        
        pygame.draw.circle(
            self.surf,
            self.color,
            (
                int(self.surf.get_width() / 2),
                int(self.surf.get_height() / 2),
            ),
            self.radius
        )
        
        self.rect = self.surf.get_rect(center=(self.x, self.y))
        
        alpha = (1 - self.frame / self.duration) * 200
        
        self.surf.set_colorkey("black")
        self.surf.set_alpha(alpha)
        
        self.x += self.vx
        self.y += self.vy
        self.radius += self.radius_growth
        self.frame += 1
        