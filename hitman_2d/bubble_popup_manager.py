import pygame

from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .game import Game
    from .npc import GameCharacter

    
@dataclass
class CounterSurface:
    counter: int
    surface: pygame.Surface
    
    def __post_init__(self) -> None:
        self.max_count = self.counter
    

class BubblePopupManager:
    
    POPUP_TRANSITION_FRAMES: int = 5
    
    def __init__(self, game: Game, character: GameCharacter):
        self.game = game
        self.character = character
        
        self.popup_queue: list[CounterSurface] = []

    def popup(self, surface: pygame.Surface, duration: int, padding: int = 5) -> None:
        bubble_surf = pygame.Surface((
            surface.get_width() + 2 * padding,
            surface.get_height() + 2 * padding + 5
        ))
        
        corner_width: int = 3
        
        bubble_outline: list[tuple[int, int]] = [
            (corner_width, 0),
            (bubble_surf.get_width() - corner_width, 0),
            (bubble_surf.get_width(), corner_width),
            (bubble_surf.get_width(), surface.get_height() + 2 * padding),
            (bubble_surf.get_width() - corner_width, surface.get_height() + 2 * padding),
            (int(bubble_surf.get_width() / 2) + corner_width, surface.get_height() + 2 * padding),
            (int(bubble_surf.get_width() / 2), surface.get_height() + 2 * padding + 5),
            (int(bubble_surf.get_width() / 2) - corner_width, surface.get_height() + 2 * padding),
            (corner_width, surface.get_height() + 2 * padding),
            (0, surface.get_height() + 2 * padding - corner_width),
            (0, corner_width)  
        ]
        
        pygame.draw.polygon(
            bubble_surf,
            [230, 230, 230],
            bubble_outline
        )
        pygame.draw.polygon(
            bubble_surf,
            [1, 1, 1],
            bubble_outline,
            width=1
        )
        
        bubble_surf.blit(
            surface,
            (
                int(bubble_surf.get_width() / 2) - int(surface.get_width() / 2),
                padding,
            )
        )
        
        count_surf = CounterSurface(counter=duration, surface=bubble_surf)
        
        self.popup_queue.append(count_surf)
        
    def draw(self) -> None:
        if not self.popup_queue: return 
        
        current_popup = self.popup_queue[0]
        
        scale: float = 1.0
        
        if 0 < current_popup.counter < self.POPUP_TRANSITION_FRAMES:
            scale = current_popup.counter / self.POPUP_TRANSITION_FRAMES
        elif current_popup.max_count - self.POPUP_TRANSITION_FRAMES <= current_popup.counter <= current_popup.max_count:
            scale = (current_popup.max_count - current_popup.counter) / self.POPUP_TRANSITION_FRAMES
        
        surf = pygame.transform.rotozoom(current_popup.surface, 0, scale=scale)
        
        surf.set_colorkey("black")
        
        self.game.window.blit(
            surf,
            self.game.camera.convert_pos((
                self.character.rect.centerx - int(surf.get_width() / 2),
                self.character.rect.top - surf.get_height() - 10
            ))
        )
        
    def update(self) -> None:
        # bla bla
        if not self.popup_queue: return
        
        first_popup = self.popup_queue[0]
        
        first_popup.counter -= 1
        
        if first_popup.counter <= 0:
            self.popup_queue.pop(0)
        