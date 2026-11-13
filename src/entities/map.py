from .mazegenerator import MazeGenerator
from .pacman import PacMan
from .ghost import Ghost, GhostFactory


class Map(MazeGenerator):
    def __init__(self, size = (15, 15), perfect = False, entry_cell = (0, 0), exit_cell = (-1, -1), seed: int = 0, ghosts: list[str] = []):
        super().__init__(size, perfect, entry_cell, exit_cell, seed)
        self.pacman: PacMan = PacMan(tuple(el // 2 for el in size))
        self.ghosts: list[Ghost] = GhostFactory().create([
            {
                "name": "blinky",
                "position": (0, 0)
            },
            {
                "name": "blinky",
                "position": size
            },
            {
                "name": "blinky",
                "position": (0, size[1])
            },
            {
                "name": "blinky",
                "position": (size[0], 0)
            }
        ])
