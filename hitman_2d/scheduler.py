from typing import Callable


class Scheduler:
    
    def __init__(self):
        self.tasks: list[tuple[int, Callable]] = []
        
    def add(self, task: Callable, schedule: int = 0, metadata=None) -> None:
        self.tasks.append([schedule, task, metadata])
        
    def update(self) -> None:
        
        for task in self.tasks[:]:
            if task[0] <= 0:
                task[1]()
                self.tasks.remove(task)
            else:
                task[0] -= 1
        
            