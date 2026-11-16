import random

class PacMan:
    def __init__(self, pos: tuple[float, float]):
        self.position: tuple[float, float] = pos
        self.direction: tuple[int, int, int, int] = (1, 0, 0, 0)
        # (N, E, S, W)
        # (1, 0, 0, 0) means looking towards north


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
