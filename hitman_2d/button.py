import pygame


class Button:
    
    all_widgets: dict[str, "Button"] = {}
    
    def __init__(
        self,
        x: int, 
        y: int, 
        key: str, 
        label: str | None = None,
        padding_x: int = 4,
        padding_y: int = 2,
        offset: int =  2
    ):
        self.x = x
        self.y = y
        self.key = key
        self.label = self.key if label is None else label
        self.offset = offset
        
        text_surf = pygame.font.SysFont("Arial", 20).render(self.label, True, "white")
        self.bg_surf = pygame.Surface((text_surf.get_width() + 2 * padding_x, text_surf.get_height() + 2 * padding_y))
        self.bg_surf.fill((50, 50, 50))
        self.bg_bottom_surf = pygame.Surface(self.bg_surf.get_size())
        self.bg_bottom_surf.fill((150, 150, 150))
        
        self.bg_bottom_rect = self.bg_bottom_surf.get_rect(topleft=(self.x, self.y))
        self.bg_rect = self.bg_surf.get_rect(topleft=(self.x, self.y - self.offset))
        
        self.bg_surf.blit(
            text_surf,
            (
                int(self.bg_surf.get_width() / 2 - (text_surf.get_width() / 2)),
                int(self.bg_surf.get_height() / 2 - (text_surf.get_height() / 2))
            )
        )
        
        self.all_widgets[self.key] = self
        
    def draw(self) -> None:
        click = pygame.mouse.get_pressed()[0]
        
        self.bg_rect.bottom = self.bg_bottom_rect.bottom - self.offset
        
        if click and self.bg_bottom_rect.collidepoint(pygame.mouse.get_pos()):
            self.bg_rect.bottom = self.bg_bottom_rect.bottom
            
        window = pygame.display.get_surface()
        window.blit(self.bg_bottom_surf, self.bg_bottom_rect)
        window.blit(self.bg_surf, self.bg_rect)
        
    def is_clicked(self) -> bool:
        if pygame.mouse.get_just_released()[0]:
            return self.bg_bottom_rect.collidepoint(pygame.mouse.get_pos())
        
        return False
    
    @property
    def rect(self) -> pygame.Rect:
        return self.bg_bottom_rect
    
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