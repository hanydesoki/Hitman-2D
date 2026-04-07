from typing import Any

import pygame


class TextDisplay:
    
    def __init__(self, text: str, x: int, y: int, size: int = 15, color: Any = "white", font_name: str = "Arial") -> None:
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font_name = font_name
        
        self.surf = pygame.font.SysFont(
            self.font_name,
            self.size
        ).render(text, True, color)
        
        
        self.rect = self.surf.get_rect(topleft=(self.x, self.y))
        
    def draw(self) -> None:
        window = pygame.display.get_surface()
        
        window.blit(self.surf, self.rect)
        
    @property
    def top(self) -> int:
        return self.rect.top
    
    @property
    def bottom(self) -> int:
        return self.rect.bottom
    
    @property
    def left(self) -> int:
        return self.rect.left
    
    @property
    def right(self) -> int:
        return self.rect.right
    
    @property
    def center(self) -> int:
        return self.rect.center

    @property
    def centerx(self) -> int:
        return self.rect.centerx

    @property
    def centery(self) -> int:
        return self.rect.centery
    
    @property
    def width(self) -> int:
        return self.rect.width
    
    @property
    def height(self) -> int:
        return self.rect.height
        