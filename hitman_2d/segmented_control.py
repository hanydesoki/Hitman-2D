import pygame


class SegmentedControl:
    
    all_widgets: list[str | "SegmentedControl"] = {}
    
    def __init__(
        self,
        options: dict[str, str],
        x: int, 
        y: int, 
        key: str, 
        label: str | None = None,
        allow_multiselect: bool = True,
        require_selection: bool = False,
        max_width: int | None = None,
        default_selection: list[str] | None = None
        
    ):  
        self.options = options
        self.x = x
        self.y = y
        self.key = key
        self.label = label
        
        self.allow_multiselect = allow_multiselect
        self.require_selection = require_selection
        
        self.selected_values: list[str] = default_selection if default_selection is not None else []
        
        if self.require_selection and len(self.selected_values) == 0 and len(self.options):
            self.selected_values.append(list(self.options)[0])
        
        self.font = pygame.font.SysFont("Arial", 20)
        
        top = self.y
        left = self.x
        
        self.options_surfs: dict[str, tuple[pygame.Surface, pygame.Surface, pygame.Rect]] = {}
        
        for key, label in self.options.items():
            text_surf_non_selected = self.font.render(label, True, "black")
            text_surf_selected = self.font.render(label, True, "white")
            
            background_surf_non_selected = pygame.Surface((text_surf_non_selected.get_width() + 4, text_surf_non_selected.get_height() + 4))
            background_surf_non_selected.fill("white")
            background_surf_non_selected.blit(
                text_surf_non_selected,
                (
                    background_surf_non_selected.get_width() / 2 - text_surf_non_selected.get_width() / 2,
                    background_surf_non_selected.get_height() / 2 - text_surf_non_selected.get_height() / 2
                )
            )
            
            background_surf_selected = pygame.Surface((text_surf_selected.get_width() + 4, text_surf_selected.get_height() + 4))
            background_surf_selected.fill("red")
            background_surf_selected.blit(
                text_surf_selected,
                (
                    background_surf_selected.get_width() / 2 - text_surf_selected.get_width() / 2,
                    background_surf_selected.get_height() / 2 - text_surf_selected.get_height() / 2
                )
            )
            
            if (left > self.x) and (left + background_surf_non_selected.get_width() > max_width):
                left = self.x
                top += background_surf_non_selected.get_height()
                
            rect = background_surf_non_selected.get_rect(topleft=(left, top))
            
            self.options_surfs[key] = (background_surf_non_selected, background_surf_selected, rect)
            left += background_surf_non_selected.get_width()
            
        self.all_widgets[self.key] = self
            
    def update(self) -> None:
        click: bool = pygame.mouse.get_just_released()[0]
        if not click: return
        
        for key, (_, __, rect) in self.options_surfs.items():
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos):
                if key in self.selected_values: # Remove option
                    if (not self.require_selection) or (len(self.selected_values) > 1 and self.require_selection):
                        self.selected_values.remove(key)     
                else: # Add / switch option
                    if not self.allow_multiselect:
                        self.selected_values.clear()
                    
                    self.selected_values.append(key)
                
            
    def draw(self) -> None:
        window = pygame.display.get_surface()
        for key, (background_surf_non_selected, background_surf_selected, rect) in self.options_surfs.items():
            surf = background_surf_selected if (key in self.selected_values) else background_surf_non_selected
            window.blit(surf, rect)
            pygame.draw.rect(window, "black", rect, 1)
            
    @property
    def bottom(self) -> None:
        return list(self.options_surfs.values())[-1][2].bottom
    
    @property
    def top(self) -> None:
        return list(self.options_surfs.values())[0][2].top
    
            
            
            
            
        
        
        
        
        