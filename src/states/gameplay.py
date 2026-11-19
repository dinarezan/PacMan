from __future__ import annotations
import pygame

from typing import Any
import time
from math import ceil
from src.core.collisions import CollisionSystem
from src.graphics.hud import Hud
from src.map.render_map import RenderMap


class Gameplay:
    """ Handle the values for a game play along the levels.

    Parameters
    ------------------------------------------
    renderer : RenderMap
        Aplication map drawing.

    lives : int
        Quantity of lives available to pacmanh.

    level : int
        Current active level in the game.

    points : int
        Total points earned along the game -> Used to load games.

    max_time : int
        Max time to play the current level.

    curr_time : int
        Current game time or time left for this level.
    """
#start = time.time()
#print("hello")
#end = time.time()
#print(end - start)

    LEVEL_TIME = 90.0
    START_LIVES = 3
    MAX_LIVES = 5

    def __init__(self,
                 renderer: RenderMap,
                 lives: int = 3,
                 level: int = 1,
                 points: int = 0,
                 max_time: float = 90,
                 curr_time: float = 0,
                 points_per_pacgum: int = 10,
                 points_per_super_pacgum: int = 50,
                 ghosts_points: int = 200):
        self.renderer = renderer
        self.hud = Hud(renderer.assets)
        self.lives = max(0, min(self.MAX_LIVES, lives))
        self.points = points
        self.fruits = 0
        self.current_level: int = level
        self.curr_time = curr_time
        self.max_time = max_time
        self.max_time = float(max_time)
        self.time_left = self.max_time
        self.time_up = False
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = ghosts_points
        self.collisions = CollisionSystem()
        self.life_lost = False
        #self.time: int = time

    @property
    def game_over(self) -> bool:
        """True when no lives are left."""
        return self.lives <= 0

    @property
    def level_complete(self) -> bool:
        """True when all normal and super pacgums have been collected."""
        game_map = self.renderer.map
        return (all(gum.eaten for gum in game_map.pacgums)
                and all(gum.eaten for gum in game_map.super_pacgums))

    def advance_level(self, renderer: RenderMap, max_time: float) -> None:
        """Switch maps while preserving the player's accumulated progress."""
        self.renderer = renderer
        self.current_level += 1
        self.max_time = float(max_time)
        self.curr_time = 0
        self.reset_time()
        self.collisions = CollisionSystem()
        self.life_lost = False

    def add_points(self, amount: int) -> None:
        """Add `amount` to the score."""
        self.points += amount

    def add_life(self) -> None:
        """Gain a life (up to `MAX_LIVES`)."""
        self.lives = min(self.MAX_LIVES, self.lives + 1)

    def lose_life(self) -> bool:
        """
        Lose a life.

        Returns
        -------
        bool
            True if Pac-Man still has lives, False on game over.
        """
        self.lives = max(0, self.lives - 1)
        return self.lives > 0

    def collect_fruit(self, points: int = 0) -> None:
        """Count a fruit eaten, optionally adding its points."""
        self.fruits += 1
        self.add_points(points)

    def activate_power_up(self, name: str,
                          duration: float | None = None) -> None:
        """
        Activate a bonus (replacing any active one).

        Parameters
        ----------
        name : str
            Sprite name in ``assets/sprites``, e.g. ``"power-up"``.
        duration : float, optional
            Seconds it lasts. If None it stays until `clear_power_up`.
        """
        self.power_up = name
        self.power_up_left = duration
        self.power_up_total = duration

    def clear_power_up(self) -> None:
        """Remove the active bonus."""
        self.power_up = None
        self.power_up_left = None
        self.power_up_total = None

    def reset_time(self) -> None:
        """Restore the level timer."""
        self.time_left = self.max_time
        self.time_up = False

    def update(self, dt: float) -> None:
        """
        Advance the timers and active gameplay.

        Nothing runs until the intro animation has finished
        (``renderer.game_init``) or after game over. The Engine does not
        call this while paused, so pausing freezes the clock.

        Parameters
        ----------
        dt : float
            Seconds since the previous frame.
        """
        self.life_lost = False
        if not self.renderer.game_init or self.game_over:
            return
        if not self.time_up:
            self.time_left = max(0.0, self.time_left - dt)
            self.time_up = self.time_left == 0.0
        if self.renderer.revealing:
            return

        game_map = self.renderer.map
        max_speed = max([game_map.pacman.speed]
                        + [ghost.speed for ghost in game_map.ghosts])
        steps = max(1, ceil(max_speed * dt / 0.1))
        step_dt = dt / steps
        if self._check_collisions():
            return
        for _ in range(steps):
            if self.life_lost:
                break
            for ghost in game_map.ghosts:
                ghost.behaviour(step_dt, game_map.pacman)
            game_map.pacman.update_position(step_dt, game_map.maze)
            if self._check_collisions():
                break
        #if self.power_up_left is not None:
        #    self.power_up_left -= dt
        #    if self.power_up_left <= 0:
        #        self.clear_power_up()

    def _check_collisions(self) -> bool:
        game_map = self.renderer.map
        contacts = self.collisions.check(
            game_map.pacman, game_map.ghosts, game_map.pacgums,
            game_map.super_pacgums)
        for gum in contacts.pacgums:
            gum.eaten = True
            self.add_points(self.points_per_pacgum)
        for sup in contacts.super_pacgums:
            sup.eaten = True
            self.add_points(self.points_per_super_pacgum)
        if contacts.ghosts:
            self.lose_life()
            self.life_lost = True
        return bool(contacts.pacgums or contacts.super_pacgums) \
            and self.level_complete

    def reset_positions(self) -> None:
        game_map = self.renderer.map
        game_map.pacman.reset_position()
        for ghost in game_map.ghosts:
            ghost.reset_position()
        self.collisions = CollisionSystem()
        self.collisions.check(game_map.pacman, game_map.ghosts,
                              game_map.pacgums, game_map.super_pacgums)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the HUD on top of the map."""
        self.hud.draw(screen, self)

# ---- PYGAME: events and drawing ---------------------------------
    def handle_event(self, event: Any) -> bool:
        """Forward a pygame event to the current menu.

        Returns
        -------
        bool
            True if the event was valid for the menu.
        """

        # ? Addd a lapse before start the game and then ctrl it.
        if (event.type == pygame.KEYDOWN and self.renderer.game_init):
            pacman = self.renderer.map.pacman
            #if pacman.speed ==
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    pacman.wanted = 0
                    return True
                elif event.key == pygame.K_d:
                    pacman.wanted = 1
                    return True
                elif event.key == pygame.K_s:
                    pacman.wanted = 2
                    return True
                elif event.key == pygame.K_a:
                    pacman.wanted = 3
                    return True
        return False

    def update_time(self, dt) -> None:
        """ Update the time in the game """
        pass





        #if (event.type == pygame.KEYDOWN
        #        and event.key == pygame.K_BACKSPACE
        #        and self.current != "main"):
        #    self.change_menu("main")
        #    return True
        #if self.current == "instructions" \
        #        and self.instructions.handle_event(event):
        #    return True
        #return self.menu.handle_event(event)