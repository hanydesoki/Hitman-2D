class TransitionValue:
    
    def __init__(self, start: float, end: float, number_frames: int, modulo_value: float = None):
        self.start = start
        self.end = end
        
        self.value = self.start
    
        self.number_frames = number_frames
        
        self.frame: int = 0
        
        self.step: float = (self.end - self.start) / self.number_frames
        
    def udpate(self) -> None:
        
        if self.done:
            self.value = self.end
        else:
            self.value += self.step
            
            self.frame += 1
        
    @property
    def done(self) -> bool:
        return self.frame >= self.number_frames