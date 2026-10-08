from typing import TYPE_CHECKING, TypedDict

import pygame

from .settings import *

if TYPE_CHECKING:
    from .game import Game


class DoorSurfaces(TypedDict):
    door_surface: pygame.Surface
    floor_surface: pygame.Surface

class Door:

    def __init__(
        self,
        game: "Game",
        x: int,
        y: int,
        rotation: int,
        surfaces: DoorSurfaces,
        trigger_rects: dict[str, pygame.Rect]
        
    ):
        self.game = game
        self.x = x
        self.y = y
        self.rotation = rotation
        self.surfaces = surfaces
        self.trigger_rects = trigger_rects
        
        self.surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE))
        self.floor_surf = pygame.Surface(self.surf.get_size())
        
        self.floor_surf.blit(self.surfaces["floor_surface"], (0, 0))
        self.floor_surf.blit(self.surfaces["floor_surface"], (TILE_SIZE, 0))
        
        self.door_1_surf = self.surfaces["door_surface"].copy()
        self.door_2_surf = pygame.transform.flip(self.surfaces["door_surface"], flip_x=True, flip_y=False)
        
        self.open_value: int = 0
        
        self.open_speed: float = 0
        
        
    def draw(self) -> None:
        
        self.surf.fill("black")
        if self.open_value != 0:
            self.surf.blit(self.floor_surf, (0, 0))
        
        self.surf.blit(self.door_1_surf, (-self.open_value, 0))
        self.surf.blit(self.door_2_surf, (TILE_SIZE + self.open_value, 0))
        
        self.game.window.blit(
            pygame.transform.rotate(self.surf, self.rotation * 90),
            (self.x, self.y)
        )
        
    def open_door(self) -> None:
        self.open_speed = 1
        
    def cloose_door(self) -> None:
        self.open_speed = -1
        
    def update(self) -> None:
        self.open_value = max(0, min(self.open_value + self.open_speed, TILE_SIZE))
        
        if (
            (self.open_speed > 0 and self.open_value >= TILE_SIZE)
            or
            (self.open_speed < 0 and self.open_value <= 0)
        ):
            self.open_speed = 0
        