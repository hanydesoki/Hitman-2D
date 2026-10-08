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
        
        self.door_opened_time: int = 0
        
        self.max_door_opened_time: int = 120
        
        
    def draw(self) -> None:
        
        self.surf.fill("black")
        if self.open_value != 0:
            self.surf.blit(self.floor_surf, (0, 0))
        
        self.surf.blit(self.door_1_surf, (-self.open_value, 0))
        self.surf.blit(self.door_2_surf, (TILE_SIZE + self.open_value, 0))
        
        self.game.window.blit(
            pygame.transform.rotate(self.surf, self.rotation * 90),
            self.game.camera.convert_pos((self.x, self.y))
        )
        
        for room_id, trigger_rect in self.trigger_rects.items():
            # print(self, trigger_rect)
            rect = trigger_rect.copy()
            rect.topleft =  self.game.camera.convert_pos(rect.topleft)
            
            pygame.draw.rect(self.game.window, "blue", rect, width=1)
            
            self.game.window.blit(
                pygame.font.SysFont("Arial", 20).render(room_id, True, "blue"),
                trigger_rect.center
            )
            
            
        
        
        
    def open_door(self) -> None:
        self.open_speed = 1
        self.door_opened_time = 0
        
    def cloose_door(self) -> None:
        self.open_speed = -1
        self.door_opened_time = 0
        
    def update(self) -> None:
        self.open_value = max(0, min(self.open_value + self.open_speed, TILE_SIZE))
        
        if (
            (self.open_speed > 0 and self.open_value >= TILE_SIZE)
            or
            (self.open_speed < 0 and self.open_value <= 0)
        ):
            self.open_speed = 0
        
        # Automatically close door
        if self.open_value >= TILE_SIZE:
            self.door_opened_time += 1
            
            if self.door_opened_time >= self.max_door_opened_time:
                self.cloose_door()
        