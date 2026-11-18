import random
from math import hypot

DIRS = {0: (0, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 0)}


class PacMan:
    def __init__(self, pos: tuple[float, float]):
        self.position: tuple[float, float] = pos
        self.cell: tuple[int, int] = (int(pos[0]), int(pos[1]))
        self.wanted: int | None = None #direction
        self.heading: int | None = None #direction
        self._next: tuple[int, int] | None = None
        self.speed: float = 1.0
        self.size: float = 1.0
        self.state: str  # * For future states.

    def update_position(self, dt: float, maze: list[list[int]]) -> None:
        """Run pacman"""

        if self._next and self.wanted == (self.heading + 2) % 4: #wanted direction is opposite
            self.cell, self._next = self._next, self.cell
            self.heading = self.wanted

        remaining = self.speed * dt # distance (in cells) to travel this frame
        while remaining > 10e-9:
            if self._next is None:
                x, y = self.cell
                new_heading = None
                for d in (self.wanted, self.heading):
                    if d is None:
                        continue
                    if (maze[y][x] >> d) & 1:
                        continue
                    new_heading = d
                    break
                self.heading = new_heading
                if self.heading is None:
                    return
                dx, dy = DIRS[self.heading]
                self._next = (x + dx, y + dy)

            nx, ny = self._next
            dx, dy = nx - self.position[0], ny - self.position[1]
            dist = hypot(dx, dy)
            if dist <= remaining: #cell is reached, set him back on exact centre
                self.position = (float(nx), float(ny))
                self.cell = self._next
                self._next = None
                remaining -= dist
            else: #move towards the cell
                f = remaining / dist
                self.position = (self.position[0] + dx * f, self.position[1] + dy * f)
                remaining = 0


class PacGum:
    def __init__(self, position: tuple[int, int]):
        self.position: tuple[int, int] = position
        self.eaten: bool = False


class SuperPacGum:
    def __init__(self, position: tuple[int, int]):
        self.position: tuple[int, int] = position
        self.eaten: bool = False

class PacGumFactory:
    @staticmethod
    def create(maze: list[list[int]], number: int, pacman_pos: tuple[int, int]) -> list[PacGum]:
        width, height = len(maze[0]), len(maze)
        indices = []
        for i in range(width):
            for j in range(height):
                if maze[j][i] != 15 and (i, j) != pacman_pos:
                    indices.append((i, j))
        corners = [(0, 0), (width - 1, 0),
                   (0, height - 1), (width - 1, height - 1)]
        for corner in corners:
            indices.remove(corner)
        positions = random.choices(indices, k=(number - 4))
        pacgums = []
        for pos in positions:
            pacgums.append(PacGum(pos))
        return pacgums

    @staticmethod
    def create_super(maze: list[list[int]]) -> list[SuperPacGum]:
        width, height = len(maze[0]), len(maze)
        corners = [(0, 0), (width - 1, 0),
                   (0, height - 1), (width - 1, height - 1)]
        super_pacgums = []
        for pos in corners:
            super_pacgums.append(SuperPacGum(pos))
        return super_pacgums
