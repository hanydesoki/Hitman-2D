class TransitionValue:
    
    def __init__(self, start: float, end: float, number_frames: int):
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
    
    
class TransitionRotation:

    def __init__(self, start: float, end: float, number_frames: int):
        """Setup the rotation animation for a character.

        Parameters
        ----------
        start : float
            Starting angle in degrees. From 0 to 360.
        end : float
            Ending angle in degrees. From 0 to 360.
        number_frames : int
            Number of frames for the rotation animation.
        modulo_value : float, optional
            description, by default None
        """

        self.start = start
        self.end = end

        self.value = self.start

        self.number_frames = number_frames

        self.frame: int = 0

        # Determine min rotation angle and its direction
        rotation_range_1 = (end - start) % 360
        rotation_range_2 = (start - end) % 360
        rotation_range = min(rotation_range_1, rotation_range_2)
        
        rotation_direction = 1 # trigonometric rotation (anticlockwise)
        if rotation_range_2 < rotation_range_1:
            rotation_direction = -1 # clockwise rotation
        
        
        self.step: float = rotation_direction * (rotation_range / self.number_frames)
        
        # print(start, end, rotation_range_1, rotation_range_2, rotation_range, rotation_direction, self.step)

    def udpate(self) -> None:

        if self.done:
            self.value = self.end
        else:
            self.value = (self.value + self.step) % 360
            self.frame += 1

    @property
    def done(self) -> bool:
        return self.frame >= self.number_frames