from .mazegenerator import MazeGenerator
from .pacman import PacMan, PacGum, PacGumFactory
from .ghost import Ghost, GhostFactory
from .models import BaseGhost


class Map(MazeGenerator):
    def __init__(self, size: tuple[int, int], pacgum: int, seed: int, ghosts: list[BaseGhost], max_time: int):
        super().__init__(size, seed)
        self.pacman: PacMan = PacMan(tuple(el // 2 for el in size))
        self.ghosts: list[Ghost] = GhostFactory().create([g.model_dump() for g in ghosts])
        self.pacgums: list[PacGum] = PacGumFactory.create(self.maze, pacgum)
        self.max_time: int = max_time
