from enum import Enum
from abc import ABC, abstractmethod
from typing import Callable, Any
from math import hypot, dist
from collections import deque
import random
from src.entities.pacman import PacMan
from src.graphics.graphic_data import Colors

DIRS = {(0, -1): 0, (1, 0): 1, (0, 1): 2, (-1, 0): 3}


class State(Enum):
    SCATTER = "scatter"     # Random movement B
    CHASE = "chase"         # Looking for pacman B
    FRIGHTENED = "frightened" # When can be eaten B moves randomly
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
        if neighbour == 0:  #open pass, no wall
            cell = tuple(map(sum, zip(position, directions[i])))
            x, y = cell
            if x < 0 or y < 0 or x >= len(maze[0]) or y >= len(maze):
                continue
            neighbours.append(cell)
        i += 1
    return neighbours


class Ghost(ABC):
    def __init__(self, pos: tuple[int, int], maze: list[list[int]], points: int, speed: float = 1):
        self.spawn_pos = pos
        self.position: tuple[int, int] = pos
        self.map_pos: tuple[float, float] = tuple(map(float, pos))
        self._next: tuple[int, int] | None = None
        self.speed: float = speed  #cells per s
        self.color: Colors
        self._maze: list[list[int]] = maze
        self.eyes: int = 4
        self.value: int = points
        self.state: State = State.SLEEP
        self._default_state = State.SLEEP
        self._rand_target = self._generate_random_target()
        self.frightened_time: float = 0.0
        self.respawn_time: float = 0.0
        random.seed()

    def reset_position(self) -> None:
        self.position = self.spawn_pos
        self.map_pos = tuple(map(float, self.spawn_pos))
        self._next = None
        self.eyes = 4
        self.state = self._default_state
        self.frightened_time = 0.0
        self.respawn_time = 0.0

    def _path_to_target(self, target: tuple[int, int]) -> list[tuple[int, int]]:
        """Generate path to target, can be pacman, corner or else."""
        start = self.position
        parents = {start: None}
        queue = deque([start])
        while queue:
            current = queue.popleft()

            if current == target:
                path = []
                node = current
                while node is not None:
                    path.append(node)
                    node = parents[node]
                return path[::-1]

            neighbours = get_neighbours(current, self._maze)
            for neighbour in neighbours:
                if neighbour not in parents:
                    parents[neighbour] = current
                    queue.append(neighbour)
        return []

    def _intercepting_path_to_target(self, target: tuple[int, int], forbidden: tuple[int, int]) -> list[tuple[int, int]]:
        """Generate a path to target from the side opposite of target's movement direction."""
        start = self.position
        parents = {start: None}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            if current == forbidden:
                continue

            if current == target:
                path = []
                node = current
                while node is not None:
                    path.append(node)
                    node = parents[node]
                return path[::-1]

            neighbours = get_neighbours(current, self._maze)
            for neighbour in neighbours:
                if neighbour not in parents:
                    parents[neighbour] = current
                    queue.append(neighbour)
        return []

    def _generate_random_target(self) -> tuple[int, int]:
        return (random.randint(0, len(self._maze[0]) - 1),
                random.randint(0, len(self._maze) - 1))

    def _random_movement(self, dt: float) -> None:
        if self.position == self._rand_target:
            self._rand_target = self._generate_random_target()
        self.hunt_target(dt, self._path_to_target, self._rand_target)

    def hunt_target(self, dt: float, pathfinder: Callable[..., list[tuple[int, int]]], *args: Any) -> None:
        """Go after target following BFS path."""
        remaining = self.speed * dt # distance (in cells) to travel this frame
        while remaining > 10e-9:
            if self._next is None:
                path = pathfinder(*args)
                if len(path) <= 1:
                    return
                self._next = path[1]
            nx, ny = self._next
            dir = tuple(map(lambda x, y: x - y, self._next, self.position))
            self.eyes = DIRS[dir]
            dx, dy = nx - self.map_pos[0], ny - self.map_pos[1]
            dist = hypot(dx, dy)
            if dist <= remaining:   # cell is reached, set him back on exact centre
                self.map_pos = (float(nx), float(ny))
                self.position = self._next
                self._next = None
                self.eyes = 4
                remaining -= dist
            else: #move towards the cell
                f = remaining / dist
                self.map_pos = (self.map_pos[0] + dx * f, self.map_pos[1] + dy * f)
                break

    def nightmare_hunt(self, dt: float, pacman: PacMan) -> None:
        target = pacman.position
        remaining = self.speed * dt
        while remaining > 10e-9:
            dx, dy = target[0] - self.map_pos[0], target[1] - self.map_pos[1]
            dist = hypot(dx, dy)
            if dist <= remaining:
                self.map_pos = target
                self.eyes = 4
                return
            else:
                f = remaining / dist
                self.map_pos = (self.map_pos[0] + dx * f, self.map_pos[1] + dy * f)
                break

    def activate_frightened(self, duration: float = 10.0) -> None:
        """Enter frightened state for the given duration (in seconds)."""
        self.state = State.FRIGHTENED
        self.frightened_time = duration

    def start_respawn(self, duration: float) -> None:
        """Return to spawn while the respawn timer counts down."""
        self.state = State.EATEN
        self.frightened_time = 0.0
        self.respawn_time = duration

    def _respawn_behaviour(self, dt: float) -> None:
        if self.state == State.EATEN:
            if self.position != self.spawn_pos:
                self.hunt_target(min(dt, self.respawn_time),
                                 self._path_to_target, self.spawn_pos)
            if self.position == self.spawn_pos:
                self.state = State.WAITING
                self._next = None
                self.eyes = 4
        self.respawn_time = max(0.0, self.respawn_time - dt)
        if self.respawn_time <= 1e-9:
            self.respawn_time = 0.0
            self.state = self._default_state

    @abstractmethod
    def behaviour(self, dt: float, pacman: PacMan) -> None:
        pass

    def default_behaviour(self, dt: float, pacman: PacMan) -> None:
        if self.state == State.SLEEP:
            self.eyes = 4
            self._next = None
        elif self.state == State.SCATTER:
            self._random_movement(dt)

        elif self.state in (State.EATEN, State.WAITING):
            self._respawn_behaviour(dt)
        elif self.state == State.NIGHTMARE:
            self.nightmare_hunt(dt, pacman)
        elif self.state == State.FRIGHTENED:
            self.frightered_behaviour(dt)
        else:
            self._random_movement(dt)

    def frightered_behaviour(self, dt: float) -> None:
        """Randomly 'run'"""
        self.frightened_time -= dt
        if self.frightened_time <= 0:
            self.state = self._default_state
            self.frightened_time = 0.0
        else:
            self._random_movement(dt)


class Blinky(Ghost):
    def __init__(self, pos: tuple[int, int], maze: list[list[int]],
                 points: int, speed: float = 0.9, chase_rad: int = 5):
        super().__init__(pos, maze, points, speed)
        self.state: State = State.SCATTER
        self._default_state: State = State.SCATTER
        self._chase_radius: int = chase_rad
        self.color: Colors = Colors.RED

    def _chase(self, dt: float, pacman_pos: tuple[int, int]) -> None:
        self._rand_target = self._generate_random_target() # IMPORTANT! prevents alternating between pacman and random target hunt
        self.hunt_target(dt, self._path_to_target, pacman_pos)

    def behaviour(self, dt: float, pacman: PacMan) -> None:
        dist_to_pacman = dist(self.map_pos, pacman.position)
        if dist_to_pacman <= self._chase_radius and self.state == State.SCATTER:
            self.state = State.CHASE
        elif dist_to_pacman > self._chase_radius and self.state == State.CHASE:
            self.state = State.SCATTER

        if self.state == State.CHASE:
            self._chase(dt, pacman.cell)
        else:
            self.default_behaviour(dt, pacman)  


class Pinky(Ghost):
    def __init__(self, pos: tuple[int, int], maze: list[list[int]], points: int,
                 speed: int = 0.9, chase_rad: int = 5):
        super().__init__(pos, maze, points, speed)
        self.state: State = State.CHASE
        self._default_state: State = State.CHASE
        self._chase_radius: int = chase_rad
        self.color: Colors = Colors.PINK
        random.seed()

    def _intercept_target(self, dt: float, pacman: PacMan) -> None:
        target = pacman._next
        if target is None:
            self.hunt_target(dt, self._path_to_target, pacman.cell)
            return
        forbidden = pacman.cell
        self.hunt_target(dt, self._intercepting_path_to_target, target, forbidden)

    def behaviour(self, dt: float, pacman: PacMan) -> None:
        if self.state == State.CHASE:
            self._intercept_target(dt, pacman)
        else:
            self.default_behaviour(dt, pacman)


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
            ghosts.append(ghost(pos, maze, points))
        return ghosts
