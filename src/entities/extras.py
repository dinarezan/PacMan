from .ghost import Ghost, get_neighbours
from .pacman import PacMan
import random

POWER_UP_PROBS = {
                "coffee": 34,
                "horror": 12,
                "gold-donu": 20,
                "clockake": 20,
}

FRUIT_VALUES = {"cherry": 100,
                "strawberry": 300,
                "orange": 500,
                "banana": 700,
                "watermelon": 1000,
                "brezel": 2000,
                "croissant": 3000,
                "pancakes": 3000,
                "chicken": 5000,
                "pizza": 10000}

FRUIT_LEVELS = {"cherry": 1,
                "strawberry": 2,
                "orange": 3,
                "banana": 4,
                "watermelon": 5,
                "brezel": 6,
                "croissant": 7,
                "pancakes": 8,
                "chicken": 9,
                "pizza": 10}


POWER_UPS = {"coffee": {"factor": 1.5, "duration": 5}}


def reachable_cells(maze: list[list[int]],
                    start: tuple[int, int]) -> list[tuple[int, int]]:
    cells = [start]
    seen = {start}
    for cell in cells:
        for neighbour in get_neighbours(cell, maze):
            if neighbour not in seen:
                seen.add(neighbour)
                cells.append(neighbour)
    return cells


class Fruit(Ghost):
    def __init__(self, name: str, maze: list[list[int]], speed: float = 2,
                 *, position: tuple[int, int] | None = None):
        if position is None:
            position = self.random_allocation(maze)
        super().__init__(position, maze, FRUIT_VALUES[name], speed)
        self.name = name
        self.visible: bool = True
        self.eaten: bool = False
        self.moving = random.choice((False, True))
        self.age = 0.0

    @staticmethod
    def random_allocation(maze: list[list[int]]) -> tuple[int, int]:
        positions = [(x, y) for y, row in enumerate(maze)
                     for x, cell in enumerate(row) if cell != 15]
        if not positions:
            raise ValueError("Cannot place a fruit in a maze without open cells")
        return random.choice(positions)

    def behaviour(self, dt: float, pacman: PacMan | None = None) -> None:
        self._random_movement(dt)

    def _generate_random_target(self) -> tuple[int, int]:
        cells = reachable_cells(self._maze, self.position)
        return random.choice(cells[1:] or cells)


class PowerUp(Fruit):
    def __init__(self, name, maze, speed = 2):
        super().__init__(name, maze, speed)
        self.power_up_factor: float = POWER_UPS[name["factor"]]
        self.duration: float = POWER_UPS[name["duration"]]

    def power_up_pacman(self) -> tuple[float, float]:
        return (self.power_up_factor, self.duration)
    # usage example when eaten: pacman.update_position(coffee.power_up_pacman())
