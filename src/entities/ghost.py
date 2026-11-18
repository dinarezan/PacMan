from enum import Enum
from abc import ABC, abstractmethod
from typing import Callable, Any
from math import hypot, dist
import random
from .pacman import PacMan


class State(Enum):
    SCATTER = "scatter"     # Random movement B
    CHASE = "chase"         # Looking for pacman B
    FRIGHTENED = "frightened" # When can be eaten
    EATEN = "eaten"         # eYES ONLY B relocate back to the corner actual BFS
    WAITING = "waiting"     # after returned into his corner for respam B do nothing in the corner
    SLEEP = "sleep"         # bEFORE START B do nothing
    NIGHTMARE = "nightmare" # Nightmare, Dina, NIGHTMARE!! B


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


class Ghost(ABC):
    def __init__(self, pos: tuple[int, int], maze: list[list[int]], speed: int = 1):
        self.spawn_pos = pos
        self.position: tuple[int, int] = pos
        self.map_pos: tuple[float, float] = tuple(map(float, pos))
        self._next: tuple[int, int] | None = None
        self.speed: int = speed #cells per s
        self.color: Color
        self._maze: list[list[int]] = maze

    def reset_position(self) -> None:
        self.position = self.spawn_pos
        self.map_pos = tuple(map(float, self.spawn_pos))
        self._next = None

    def _path_to_target(self, target: tuple[int, int]) -> list[tuple[int, int]]:
        """Generate path to target, can be pacman, corner or else."""
        visited: list[list[tuple[int, int]]] = []
        visited.append([self.position])
        path: list[tuple[int, int]] = []
        valid_paths: list[list[tuple[int,int]]] = []
        while visited:
            path = visited.pop(0)
            current = path[-1]

            if current == target:
                valid_paths.append(path)
                break

            neighbours = get_neighbours(current, self._maze)
            for neighbour in neighbours:
                if neighbour not in path:
                    new_path = list(path)
                    new_path.append(neighbour)
                    visited.append(new_path)
        if not valid_paths:
            raise IndexError(f"{self.__class__.__name__} cannot find a path to pacman.")
        return valid_paths.pop(0)

    def _intercepting_path_to_target(self, target: tuple[int, int], forbidden: tuple[int, int]) -> list[tuple[int, int]]:
        """Generate a path to target from the side opposite of target's movement direction."""
        visited: list[list[tuple[int, int]]] = []
        visited.append([self.position])
        path: list[tuple[int, int]] = []
        valid_paths: list[list[tuple[int,int]]] = []
        while visited:
            path = visited.pop(0)
            current = path[-1]
            if current == forbidden:
                continue

            if current == target:
                valid_paths.append(path)
                break

            neighbours = get_neighbours(current, self._maze)
            for neighbour in neighbours:
                if neighbour not in path:
                    new_path = list(path)
                    new_path.append(neighbour)
                    visited.append(new_path)
        if not valid_paths:
            return []
            # raise IndexError(f"{self.__class__.__name__} cannot find a path to pacman.")
        return valid_paths.pop(0)

    def hunt_target(self, dt: float, target: tuple[int, int], pathfinder: Callable[..., list[tuple[int, int]]], *args: Any) -> None:
        """Go after target following BFS path."""
        remaining = self.speed * dt # distance (in cells) to travel this frame
        while remaining > 10e-9:
            if self._next is None:
                path = pathfinder(*args)
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

    @abstractmethod
    def behaviour(self, dt: float, pacman: PacMan) -> None:
        pass


class Blinky(Ghost):
    def __init__(self, pos: tuple[int, int], maze: list[list[int]], speed: int = 0.9, chase_rad: int = 1):
        super().__init__(pos, maze, speed)
        self.state: State = State.CHASE
        self._chase_radius: int = chase_rad
        self.color: Color
        self._rand_target = self._generate_random_target()
        random.seed()

    def _generate_random_target(self) -> tuple[int, int]:
        return (random.randint(0, len(self._maze[0]) - 1),
                random.randint(0, len(self._maze) - 1))

    def _chase(self, dt: float, pacman_pos: tuple[int, int]) -> None:
        self._rand_target = self._generate_random_target() # IMPORTANT! prevents alternating between pacman and random target hunt
        self.hunt_target(dt, pacman_pos, self._path_to_target, pacman_pos)

    def behaviour(self, dt: float, pacman: PacMan) -> None:
        dist_to_pacman = dist(self.map_pos, pacman.position)
        if dist_to_pacman <= self._chase_radius and self.state == State.CHASE:
            self._chase(dt, pacman.cell)
        else:
            if self.position == self._rand_target:
                self._rand_target = self._generate_random_target()
            self.hunt_target(dt, self._rand_target, self._path_to_target, self._rand_target)


class Pinky(Ghost):
    def __init__(self, pos: tuple[int, int], maze: list[list[int]], speed: int = 0.9, chase_rad: int = 5):
        super().__init__(pos, maze, speed)
        self.state: State = State.CHASE
        self._chase_radius: int = chase_rad
        self.color: Color
        random.seed()

    def _intercept_target(self, dt: float, pacman: PacMan) -> None:
        target = pacman._next
        if target is None:
            self.hunt_target(dt, pacman.cell, self._path_to_target, pacman.cell)
            return
        forbidden = pacman.cell
        self.hunt_target(dt, target, self._intercepting_path_to_target, target, forbidden)

    def behaviour(self, dt: float, pacman: PacMan) -> None:
        if self.state == State.CHASE:
            self._intercept_target(dt, pacman)



class GhostFactory:
    registry: dict[str, type[Ghost]] = {
        "blinky": Blinky,
        "pinky": Pinky
    }

    def create(self, base_ghosts: list[dict[str, tuple[int, int]]], maze: list[list[int]], points: int) -> list[Ghost]:
        ghosts = []
        for g in base_ghosts:
            name = g.get("name")
            pos = g.get("position")
            ghost = self.registry.get(name)
            ghosts.append(ghost(pos, maze))
        return ghosts
