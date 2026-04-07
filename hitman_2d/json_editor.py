import pygame

from .text_display import TextDisplay
from .text_field import TextField


class JSONEditor:
    
    def __init__(
        self,
        obj: dict,
        x: int,
        y: int,
        width: int,
        key: str,
        
        attribute_options: dict[str, dict] = None,
        
        
    ):
        self.obj = obj
        self.x = x
        self.y = y
        self.width = width
        self.key = key
        
        self.attribute_options = {key: {} for key in obj} | ({} if attribute_options is None else attribute_options)
        
        self.widgets: dict[str, tuple[TextDisplay, TextField]] = {}

        top: int = y
        
        
        for key, attr_infos in self.attribute_options.items():
            label: str = attr_infos.get("label", key)
            
            text_display = TextDisplay(
                text=label,
                x=x,
                y=top
            )
            text_field = TextField(
                x=text_display.right + 10,
                y=top,
                width=self.width - text_display.width - 10,
                height=text_display.height,
                key=f"{self.key}___{key}",
                default_text=str(obj[key])
            )
            
            self.widgets[key] = (text_display, text_field)
            
            top = max(text_display.bottom, text_field.bottom) + 2
            
    def draw(self) -> None:
        for text_display, text_field in self.widgets.values():
            text_display.draw()
            text_field.draw()
            
    def update(self, all_events: list[pygame.Event]) -> None:
        for _, text_field in self.widgets.values():
            text_field.udpate(all_events)
    
            
            