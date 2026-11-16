from .mazegenerator import MazeGenerator
from .pacman import PacMan, PacGum, SuperPacGum, PacGumFactory
from .ghost import Ghost, GhostFactory
from .models import BaseGhost
from numpy.typing import NDArray
import numpy as np


class Map(MazeGenerator):
    def __init__(self, size: tuple[int, int], pacgum: int, seed: int, ghosts: list[BaseGhost], max_time: int):
        super().__init__(size=size, seed=seed, perfect=False)
        self.pacman: PacMan = self._position_pacman(size)
        self.ghosts: list[Ghost] = GhostFactory().create([g.model_dump() for g in ghosts], self.maze)
        self.pacgums: list[PacGum] = PacGumFactory.create(self.maze, pacgum, self.pacman.position)
        self.super_pacgums: list[SuperPacGum] = PacGumFactory.create_super(self.maze)
        self.max_time: int = max_time

    def _position_pacman(self, size: tuple[int, int]) -> PacMan:
        x, y = tuple(el // 2 for el in size)
        if size[0] % 2 == 0:
            x = size[0] // 2 - 1
        return PacMan((x, y))

    def hex_to_binary(self) -> NDArray:
        size = (self._height * 2 + 1, self._width * 2 + 1)
        bin_map = np.zeros(size, dtype=int)
        bin_map[0::2, 0::2] = 1

        for i in range(self._height):
            for j in range(self._width):
                val = self.maze[i][j]
                r, c = 2 * i + 1, 2 * j + 1      # cell centre
                bin_map[r - 1, c] = val & 1         # North
                bin_map[r, c + 1] = (val >> 1) & 1  # East
                bin_map[r + 1, c] = (val >> 2) & 1  # South
                bin_map[r, c - 1] = (val >> 3) & 1  # West
        return bin_map

    def get_ghost_movement(self) -> None:
        print(self.maze)
        print(self.pacman.position)
        x, y = self.pacman.position
        print(self.maze[y][x])
        for ghost in self.ghosts:
            print(f"Ghost on postion {ghost.position} path:")
            ghost.path_to_target(tuple(map(round, self.pacman.position)), self.maze)