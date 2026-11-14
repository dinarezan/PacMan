from .mazegenerator import MazeGenerator
from .pacman import PacMan, PacGum, PacGumFactory
from .ghost import Ghost, GhostFactory
from .models import BaseGhost
from numpy.typing import NDArray
import numpy as np


class Map(MazeGenerator):
    def __init__(self, size: tuple[int, int], pacgum: int, seed: int, ghosts: list[BaseGhost], max_time: int):
        super().__init__(size, seed)
        self.pacman: PacMan = PacMan(tuple(el // 2 for el in size))
        self.ghosts: list[Ghost] = GhostFactory().create([g.model_dump() for g in ghosts])
        self.pacgums: list[PacGum] = PacGumFactory.create(self.maze, pacgum)
        self.max_time: int = max_time

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
