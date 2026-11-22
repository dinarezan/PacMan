from .ghost import Ghost
import random

FRUIT_VALUES = {"cherry": 20,
                "strawberry": 20,
                "orange": 20,
                "banana": 20,
                "watermelon": 20,
                "pretzel": 20,
                "croissant": 20,
                "pancakes": 20,
                "chicken": 20,
                "pizza": 100000}


POWER_UPS = {"coffee": {"factor": 1.5, "duration": 5}}

class Fruit(Ghost):
    def __init__(self, name: str, maze: list[list[int]], speed: float = 2):
        super().__init__(self.random_allocation(maze), maze, FRUIT_VALUES.get(name), speed)
        self.visible: bool = True
        self.eaten: bool = False

    def random_allocation(self, maze: list[list[int]]) -> None:
        width = len(maze[0]) - 1
        height = len(maze) - 1
        x = random.randint(0, width)
        y = random.randint(0, height)
        if (x, y) in [(0, 0), (width, 0), (0, height), (width, height)]:
            self.random_allocation(maze)
        return (x, y)

    def behaviour(self, dt) -> None:
        self._random_movement(dt)


class PowerUp(Fruit):
    def __init__(self, name, maze, speed = 2):
        super().__init__(name, maze, speed)
        self.power_up_factor: float = POWER_UPS[name["factor"]]
        self.duration: float = POWER_UPS[name["duration"]]

    def power_up_pacman(self) -> tuple[float, float]:
        return (self.power_up_factor, self.duration)
    # usage example when eaten: pacman.update_position(coffee.power_up_pacman())
