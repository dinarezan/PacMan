from dataclasses import dataclass
from math import dist

from src.entities.ghost import Ghost
from src.entities.pacman import PacGum, PacMan, SuperPacGum


@dataclass
class Collisions:
    ghosts: list[Ghost]
    pacgums: list[PacGum]
    super_pacgums: list[SuperPacGum]


class CollisionSystem:
    """Detect new ghost contacts and uneaten pacgums in map-cell units."""

    GHOST_DISTANCE = 0.5
    PACGUM_DISTANCE = 0.3

    def __init__(self) -> None:
        self._touching_ghosts: set[Ghost] = set()

    def check(self, pacman: PacMan, ghosts: list[Ghost],
              pacgums: list[PacGum],
              super_pacgums: list[SuperPacGum]) -> Collisions:
        touching = {ghost for ghost in ghosts
                    if dist(pacman.position, ghost.map_pos)
                    <= self.GHOST_DISTANCE}
        new_ghosts = [ghost for ghost in ghosts
                      if ghost in touching and ghost not in self._touching_ghosts]
        self._touching_ghosts = touching
        return Collisions(
            ghosts=new_ghosts,
            pacgums=[gum for gum in pacgums if not gum.eaten
                     and dist(pacman.position, gum.position)
                     <= self.PACGUM_DISTANCE],
            super_pacgums=[gum for gum in super_pacgums if not gum.eaten
                           and dist(pacman.position, gum.position)
                           <= self.PACGUM_DISTANCE],
        )
