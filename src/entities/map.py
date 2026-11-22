from .mazegenerator import MazeGenerator
from .pacman import PacMan, PacGum, SuperPacGum, PacGumFactory
from .ghost import Ghost, GhostFactory
from .models import BaseGhost
from numpy.typing import NDArray
import numpy as np


class Map(MazeGenerator):
    def __init__(self,
                 size: tuple[int, int],
                 pacgum: int,
                 seed: int,
                 ghosts: list[BaseGhost],
                 max_time: int,
                 points_per_pacgum: int,
                 points_per_super_pacgum: int,
                 points_per_ghost: int
                 ):
        super().__init__(size=size, seed=seed, perfect=False)
        self.pacman: PacMan = self._position_pacman(size)
        self.ghosts: list[
            Ghost] = GhostFactory().create([g.model_dump() for g in ghosts],
                                           self.maze,
                                           points_per_ghost)
        self.pacgums: list[
            PacGum] = PacGumFactory.create(self.maze, pacgum,
                                           self.pacman.position,
                                           points_per_pacgum)
        self.super_pacgums: list[
            SuperPacGum] = PacGumFactory.create_super(self.maze,
                                                      points_per_super_pacgum)
        self.max_time: int = max_time

    def _position_pacman(self, size: tuple[int, int]) -> PacMan:
        x, y = tuple(el // 2 for el in size)
        if size[0] % 2 == 0:
            x = size[0] // 2 - 1
        return PacMan((x, y))

