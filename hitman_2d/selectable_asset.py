import pygame


class SelectableAsset:
    
    all_widgets: dict[str, "SelectableAsset"] = {}
    
    def __init__(
        self,
        x: int, 
        y: int,
        surf: pygame.Surface,
        key: str, 
        label: str | None = None,
        colorkey = None
    ):
        self.x = x
        self.y = y
        self.key = key
        self.surf = surf.copy()
        
        if colorkey is not None:
            self.surf.set_colorkey(colorkey)
        
        self.label = self.key if label is None else label
        
        self.rect = self.surf.get_rect(topleft=(x, y))
        
        self.all_widgets[self.key] = self
        
    def draw(self) -> None:  
        window = pygame.display.get_surface()
        mouse_pos = pygame.mouse.get_pos()
        
        window.blit(self.surf, self.rect)
        
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                window,
                "white",
                self.rect,
                1
            )
        
    def is_clicked(self) -> bool:
        if pygame.mouse.get_just_released()[0]:
            return self.rect.collidepoint(pygame.mouse.get_pos())
        
        return False
    
    
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
    
class ToggleableAsset(SelectableAsset):
    
    def __init__(self, x, y, surf, key, label = None, colorkey=None, toggled: bool = False):
        super().__init__(x, y, surf, key, label, colorkey)
        
        self.toggled = toggled
        
    def toggle(self) -> None:
        self.toggled = not self.toggled
        
    def draw(self):
        self.surf.set_alpha(255 if self.toggled else 100)
        super().draw()