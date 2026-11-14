from enum import Enum
from abc import ABC


class State(Enum):
    SCATTER = "scatter"
    CHASE = "chase"
    FRIGHTENED = "frightened"
    EATEN = "eaten"
    SLEEP = "sleep"


class Ghost(ABC):
    def __init__(self, pos: tuple[int, int], speed: int):
        self.position: tuple[int, int] = pos
        self.map_pos: tuple[float, float] = pos
        self.speed: int = speed
        self.color: Color

    def path_to_target(self, target: tuple[int, int]) -> list[tuple[int, int]]:
        """Generate path to target, can be pacman, corner or else."""
        pass


class Blinky(Ghost):
    def __init__(self, pos: tuple[int, int], speed: int = 1):
        super.__init__(pos, speed)
        self.state: State = State.CHASE
        self.color: Color

    def behaviour(self, pacman_pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Hunt pacman"""
        self.path_to_target(pacman_pos)


class GhostFactory:
    registry: dict[str, type[Ghost]] = {
        "blinky": Blinky
    }

    def create(self, ghosts: list[dict[str, tuple[int, int]]]) -> list[Ghost]:
        ghosts = []
        for g in ghosts:
            name = g.get("name")
            pos = g.get("position")
            ghost = self.registry.get(name)
            ghosts.append(ghost(pos=pos))
        return ghosts
