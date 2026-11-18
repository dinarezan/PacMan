from dataclasses import dataclass
from math import dist


from src.entities.ghost import Ghost
from src.entities.pacman import PacGum, PacMan, SuperPacGum


@dataclass
class Collisions:
    ghosts: list[Ghost]
    pacgums: list[PacGum]
    super_pacgums: list[SuperPacGum]

    # * Available in the next Edition of PACMAN GAMES!!
    # * When Dina decided is more important Pacman than eat.
    # fruits: list(Fruits)
    # power_ups: list(PowerUps)


class CollisionSystem:
    """ Detect new ghost contacts, uneaten pacgums (by Dina) in map-cell."""

    # To check when affects or not
    GHOST_DISTANCE = 0.5
    PACGUM_DISTANCE = 0.1

    def __init__(self) -> None:
        self._touching_ghosts: set[Ghost] = set()

    def check(self,
              pacman: PacMan,
              ghosts: list[Ghost],
              pacgums: list[PacGum],
              super_pacgums: list[SuperPacGum]
              ) -> Collisions:
        touching = {ghost for ghost in ghosts
                    if dist(pacman.position, ghost.map_pos)
                    <= self.GHOST_DISTANCE}

        # TODO EDU must add for check the state of the ghost if is collision here or wathever
        # Create a list with all danger States
        # Check: and ghost.state in danger_state: [States]
        new_ghosts = [ghost for ghost in ghosts
                      if ghost in touching and ghost
                      not in self._touching_ghosts]
        new_pacgums = [gum for gum in pacgums if not gum.eaten
                       and dist(pacman.position, gum.position)
                       <= self.PACGUM_DISTANCE]
        new_supgums = [sup for sup in super_pacgums if not sup.eaten
                       and dist(pacman.position, sup.position)
                       <= self.PACGUM_DISTANCE]

        self._touching_ghosts = touching
        return Collisions(
              ghosts=new_ghosts,
              pacgums=new_pacgums,
              super_pacgums=new_supgums,
        )


#for event in pygame.event.get():
#        if event.type == pygame.QUIT:
#            run = False

#    sprite1.rect.center = Pacman_sprite
#    collide = pygame.sprite.spritecollide(sprite1, test_group, False, pygame.sprite.collide_circle)

#    Action()
