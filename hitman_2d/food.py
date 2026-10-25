from typing import TYPE_CHECKING
import random

import pygame

from .smoke_particles import SmokeParticle

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
        
        self.smoke_particles: list[SmokeParticle] = []
        
    def draw(self) -> None:
        self.update_particles()
        
        self.game.window.blit(
            self.surf,
            self.game.camera.convert_pos(self.rect.topleft)
        )
        
        # TODO: Draw particles if poisonned
        # if self.poisonned:
        for particle in self.smoke_particles:
            particle.draw()
        
    def update_particles(self) -> None:
        # if not self.poisonned: return
        
        if self.poisonned and random.random() < 0.1:
            smoke_particle = SmokeParticle(
                game=self.game,
                x=self.rect.centerx + random.randint(-3, 3),
                y=self.rect.centery + random.randint(-3, 3),
                radius=1 + random.random() * 2,
                duration=random.randint(1, 3) * 60,
                color=self.poison_colors[self.poison]
            )
            self.smoke_particles.append(smoke_particle)
        
        new_smoke_particles: list[SmokeParticle] = []
        
        for sp in self.smoke_particles:
            sp.update()
            if sp.active:
                new_smoke_particles.append(sp)
            
        self.smoke_particles = new_smoke_particles
        
    
    @property
    def poisonned(self) -> bool:
        return self.poison != 0