from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .game import Game

import pygame


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