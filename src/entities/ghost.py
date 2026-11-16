from enum import Enum
from abc import ABC
from math import hypot


class State(Enum):
    SCATTER = "scatter"
    CHASE = "chase"
    FRIGHTENED = "frightened"
    EATEN = "eaten"
    SLEEP = "sleep"


class Ghost(ABC):
    def __init__(self, pos: tuple[int, int], speed: int = 1):
        self.position: tuple[int, int] = pos
        self.map_pos: tuple[float, float] = tuple(map(float, pos))
        self._next: tuple[int, int] | None = None
        self.speed: int = speed #cells per s
        self.color: Color

    def _path_to_target(self, target: tuple[int, int], maze: list[list[int]]) -> list[tuple[int, int]]:
        """Generate path to target, can be pacman, corner or else."""

        def get_neighbours(position: tuple[int, int], maze: list[list[int]]) -> list[tuple[int, int]]:
            x, y = position
            cell = maze[y][x]

            n = cell & 1
            e = (cell >> 1) & 1
            s = (cell >> 2) & 1
            w = (cell >> 3) & 1

            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] #NESW
            neighbours = []
            i = 0
            for neighbour in [n, e, s, w]:
                if neighbour == 0: #open pass, no wall
                    cell = tuple(map(sum, zip(position, directions[i])))
                    x, y = cell
                    if x < 0 or y < 0 or x >= len(maze[0]) or y >= len(maze):
                        continue
                    neighbours.append(cell)
                i += 1
            return neighbours

        visited: list[list[tuple[int, int]]] = []
        visited.append([self.position])
        path: list[tuple[int, int]] = []
        valid_paths: list[list[tuple[int,int]]] = []
        while visited:
            path = visited.pop(0)
            current = path[-1]

            if current == target:
                valid_paths.append(path)
                continue

            neighbours = get_neighbours(current, maze)
            for neighbour in neighbours:
                if neighbour not in path:
                    new_path = list(path)
                    new_path.append(neighbour)
                    visited.append(new_path)
        print(f"{len(valid_paths)} valid paths found")
        return valid_paths.pop(0)

    def update_position(self, dt: float, target: tuple[int, int], maze: list[list[int]]) -> None:
        """Hunt pacman"""
        remaining = self.speed * dt # distance (in cells) to travel this frame
        while remaining > 10e-9:
            if self._next is None:
                path = self._path_to_target(target, maze)
                if len(path) <= 1:
                    return
                self._next = path[1]
            nx, ny = self._next
            dx, dy = nx - self.map_pos[0], ny - self.map_pos[1]
            dist = hypot(dx, dy)
            if dist <= remaining: #cell is reached, set him back on exact centre
                self.map_pos = (float(nx), float(ny))
                self.position = self._next
                self._next = None
                remaining -= dist
            else: #move towards the cell
                f = remaining / dist
                self.map_pos = (self.map_pos[0] + dx * f, self.map_pos[1] + dy * f)
                remaining = 0


class Blinky(Ghost):
    def __init__(self, pos: tuple[int, int], speed: int = 1):
        super().__init__(pos, speed)
        self.state: State = State.CHASE
        self.color: Color


class GhostFactory:
    registry: dict[str, type[Ghost]] = {
        "blinky": Blinky
    }

    def create(self, base_ghosts: list[dict[str, tuple[int, int]]]) -> list[Ghost]:
        ghosts = []
        for g in base_ghosts:
            name = g.get("name")
            pos = g.get("position")
            ghost = self.registry.get(name)
            ghosts.append(ghost(pos))
        return ghosts
