from typing import Any

import pygame


class TextField:
    
    all_widgets: dict[str, "TextField"] = {}
    
    cursor_duration: int = 45
    
    def __init__(
        self,
        x: int, 
        y: int, 
        width: int, 
        height: int,
        key: str,
        size: int = 15,
        font_name: str = "Arial",
        text_color: Any = "black",
        background_color: Any = "white",
        default_text: str = "" 
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.key = key
        
        self.size = size
        self.font_name = font_name
        self.text_color = text_color
        self.background_color = background_color
        
        self.text = default_text
        
        self.active: bool = False
        
        self.surf = pygame.Surface((self.width, self.height))
        self.surf.fill(self.background_color)
        
        self.rect = self.surf.get_rect(topleft=(self.x, self.y))
        
        self.font = pygame.font.SysFont(self.font_name, self.size)
        
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(midleft=(self.rect.midleft[0] + 3, self.rect.midleft[1]))
        
        self.frame: int = 0
        
        self.has_changed: bool = False
        
        self.all_widgets[key] = self
            
    
    def focus(self) -> None:
        for textfield in self.all_widgets.values():
            textfield.unfocus()
        self.active = True
            
    def unfocus(self) -> None:
        self.active = False
        self.frame = 0
        
    def update_rects(self) -> None:
        text = self.text
        
        self.text_surf = self.font.render(text, True, self.text_color)
        while self.text_surf.get_width() > self.width and text:
            text = text[1:]
            self.text_surf = self.font.render(text, True, self.text_color)
        
        self.text_rect = self.text_surf.get_rect(midleft=(self.rect.midleft[0] + 3, self.rect.midleft[1]))
    
    def is_clicked(self) -> bool:
        if pygame.mouse.get_just_released()[0]:
            return self.rect.collidepoint(pygame.mouse.get_pos())
        
        return False
    
    def check_outside_click(self) -> None:
        if pygame.mouse.get_just_released()[0] and not self.rect.collidepoint(pygame.mouse.get_pos()):
            self.unfocus()
        
    def udpate(self, all_events: list[pygame.Event]) -> None:
        
        self.has_changed = False
        
        if self.is_clicked():
            self.focus()
        
        self.check_outside_click()
        
        if not self.active: return
        
        for event in all_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_SPACE:
                    self.text = self.text + " "
                else:
                    self.text += event.unicode
                    
                self.update_rects()
                self.has_changed = True
                
        self.frame = (self.frame + 1) % (self.cursor_duration * 2)
        
    def draw(self) -> None:
        window = pygame.display.get_surface()
        
        window.blit(self.surf, self.rect)
        window.blit(self.text_surf, self.text_rect)
        
        if self.active and (self.frame / self.cursor_duration) < 1:
            pygame.draw.line(
                window,
                self.text_color,
                (self.text_rect.topright[0] + 1, self.text_rect.topright[1] + 2),
                (self.text_rect.bottomright[0] + 1, self.text_rect.bottomright[1] - 2),
            )
            
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
        
   
    @classmethod
    def active_field(cls) -> "TextField" | None:
        for text_field in cls.all_widgets.values():
            if text_field.active: return text_field
            
        return None
        
        
        
        
        
        