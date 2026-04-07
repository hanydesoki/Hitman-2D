import random


class Camera:
    
    def __init__(self):
        self.x: float = 0
        self.y: float = 0
        
        self.offset_x: float = 0
        self.offset_y: float = 0
        
        self.shake_magnitude: float = 0
        self.shake_decrement: float = 1
        
    def convert_pos(self, pos: tuple[float, float]) -> tuple[float, float]:
        return pos[0] - self.x + self.offset_x, pos[1] - self.y + self.offset_y
    
    def shake(self, magnitude: float, decrement: float = 1) -> None:
        self.shake_magnitude = magnitude
        self.shake_decrement = decrement
    
    def update(self) -> None:
        
        if self.shake_magnitude:
            self.offset_x = random.choice([1, -1]) * self.shake_magnitude
            self.offset_y = random.choice([1, -1]) * self.shake_magnitude
        
        self.shake_magnitude = max(0, self.shake_magnitude - self.shake_decrement)
        