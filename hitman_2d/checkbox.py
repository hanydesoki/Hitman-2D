import pygame

from .text_display import TextDisplay


class Checkbox:
    
    all_widgets: dict[str, "Checkbox"] = {}
    
    def __init__(
            self,
            x: int, 
            y: int, 
            key: str, 
            label: str | None = None,
            default_value: bool = False,
            checkbox_size: int = 20,
            checked_color: tuple[int, int, int] = (255, 0, 0),
            unchecked_color: tuple[int, int, int] = (255, 255, 255)
        ):

        self.x = x
        self.y = y
        self.key = key
        self.label = self.key if label is None else label
        self._value = default_value
        self.checkbox_size = checkbox_size
        self.checked_color = checked_color
        self.unchecked_color = unchecked_color
        
        
        self.surf: pygame.Surface = pygame.Surface((checkbox_size, checkbox_size))
        self.checbox_rect = self.surf.get_rect(topleft=(x, y))
        self.text_display = TextDisplay(self.label, self.x + checkbox_size + 20, self.y)
        self.text_display.rect.centery = self.checbox_rect.centery
        
        self.rect = pygame.Rect(
            self.checbox_rect.left, 
            min(self.checbox_rect.top, self.text_display.top),
            self.text_display.right - self.checbox_rect.left,
            max(self.checbox_rect.bottom, self.text_display.bottom) - min(self.checbox_rect.top, self.text_display.top)
        )
        
        self.surf.fill(checked_color if self.value else unchecked_color)
        
        
        self.all_widgets[key] = self
        
        self.clicked: bool = False
        
    def is_clicked(self) -> bool:
        if pygame.mouse.get_just_released()[0]:
            mouse_pos = pygame.mouse.get_pos()
            # return self.checbox_rect.collidepoint(mouse_pos) or self.text_display.rect.collidepoint(mouse_pos)
            return self.rect.collidepoint(mouse_pos)
        
        return False
    
    def draw(self) -> None:
        window = pygame.display.get_surface()
        
        window.blit(self.surf, self.checbox_rect)
        self.text_display.draw()
    
    def update(self) -> None:
        self.clicked = False
        if self.is_clicked():
            self.value = not self.value
            self.clicked = True
            self.surf.fill(self.checked_color if self.value else self.unchecked_color)
    
    @property
    def value(self) -> bool:
        return self._value
    
    @value.setter
    def value(self, new_value: bool) -> None:
        self._value = bool(new_value)
        
        self.surf.fill(self.checked_color if self.value else self.unchecked_color)
    
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