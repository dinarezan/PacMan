from __future__ import annotations
import pygame

import random
from typing import Any
import time
from math import ceil, hypot
from src.core.collisions import CollisionSystem
from src.graphics.hud import Hud
from src.map.render_map import RenderMap
from src.entities.extras import (FRUIT_LEVELS, POWER_UP_PROBS, Fruit, PowerUp,
                                 reachable_cells)
from src.entities.ghost import Ghost, State, Blinky


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
    FRIGHTENED_TIME = 10.0
    RESPAWN_TIME = 10.0
    FRUIT_LIFETIME = 25.0
    FRUIT_SPEED = 2.0
    FLASH_MODE_SPEED = 4.5
    # --  DASH  -------------------------
    DASH_DURATION = 0.8
    DASH_COOLDOWN = 15.0
    DASH_SPEED = 10.0
    # --  POWER UPS  ----------------------------
    POWER_UP_INTERVAL = 40              # Dots required to Spam it
    POWER_UP_CHANCE = 0.4               # Probs to spam it when interval
    POWER_UP_DURATION = 40.0            # Effects duration
    CLOCKAKE_EFFECT = 0.8               # Ghost speed effect
    GOLD_DONUT_EFFECT = 1.3             # Frightered duration increaase
    COFFEE_EFFECT = 1.25                # Speed effect
    HORROR_EFFECT = 0.85                # Slow effect
    BOLD_EFFECT = 50.0                  # Dash cold retudction
    BEHELIT_EFFECT = 1.4                # Speed increment on Ghosts
    SPECIAL_DURATION = 15               # Duration for Behelit and star

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
        self.starting_lives = self.lives
        self.invincible = False
        self.immortality = False
        self.flash_mode = False
        self.no_dash_cooldown = False
        self.dash_remaining = 0.0
        self.dash_cooldown_remaining = 0.0
        self._dash_cooldown_reduced = False
        self._cooldown_frame_remaining = 0.0
        self.points = points
        self.fruits = 0
        self._fruit_spawned = False
        self.renderer.map.fruit = None
        self.renderer.map.extra_fruits = []
        self.renderer.map.power_ups = []
        self.pacgums_eaten = 0
        self.power_up: str | None = None
        self.power_up_left: float | None = None
        self.power_up_total: float | None = None
        self.gold_donut_active = False
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
        self._end_dash()
        self.clear_power_up()
        self.gold_donut_active = False
        self.renderer = renderer
        self.renderer.map.fruit = None
        self.renderer.map.extra_fruits = []
        self.renderer.map.power_ups = []
        self.pacgums_eaten = 0
        self._fruit_spawned = False
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
        self.clear_power_up()
        self.gold_donut_active = False
        if self.immortality:
            self.lives = self.starting_lives
        else:
            self.lives = max(0, self.lives - 1)
        return self.lives > 0

    def set_cheat(self, name: str, enabled: bool) -> None:
        """Set a cheat for this game, without changing its base speed."""
        if name == "invincible":
            self.invincible = enabled
            self.collisions = CollisionSystem()
        elif name == "immortality":
            self.immortality = enabled
            if enabled:
                self.lives = self.starting_lives
        elif name == "flash_mode":
            self.flash_mode = enabled
        elif name == "no_dash_cooldown":
            self.no_dash_cooldown = enabled
            if enabled:
                self.dash_cooldown_remaining = 0.0
        else:
            raise ValueError(f"Unknown cheat: {name!r}")

    def collect_fruit(self, points: int = 0) -> None:
        """Count a fruit eaten, optionally adding its points."""
        self.fruits += 1
        self.add_points(points)

    def activate_power_up(self, name: str,
                          duration: float | None = None) -> None:
        """Activate a power-up; timed bonuses replace each other."""
        if name not in POWER_UP_PROBS:
            raise ValueError(f"Unknown power-up: {name!r}")
        if name == "gold-donut":
            self.gold_donut_active = True
            return
        if duration is None:
            duration = (self.SPECIAL_DURATION if name in ("behelit", "star")
                        else self.POWER_UP_DURATION)
        if duration <= 0:
            raise ValueError("Power-up duration must be positive")
        self.clear_power_up()
        game_map = self.renderer.map
        game_map.pacman.active_power_up = name
        self.power_up = name
        self.power_up_left = duration
        self.power_up_total = duration
        if name == "bold" and not self._dash_cooldown_reduced:
            if self.dash_cooldown_remaining > 0:
                self.dash_cooldown_remaining *= 1 - self.BOLD_EFFECT / 100
                self._dash_cooldown_reduced = True
        if name in ("clockake", "behelit"):
            factor = (self.CLOCKAKE_EFFECT if name == "clockake"
                      else self.BEHELIT_EFFECT)
            for ghost in self.renderer.map.ghosts:
                ghost.speed_multiplier = factor

    def clear_power_up(self) -> None:
        """Remove the active bonus."""
        game_map = self.renderer.map
        game_map.pacman.active_power_up = None
        self.power_up = None
        self.power_up_left = None
        self.power_up_total = None
        for ghost in self.renderer.map.ghosts:
            ghost.speed_multiplier = 1.0

    def reset_time(self) -> None:
        """Restore the level timer."""
        self.time_left = self.max_time
        self.time_up = False

    def _start_dash(self) -> None:
        if self.dash_cooldown_remaining > 0:
            return
        self.dash_remaining = self.DASH_DURATION
        self._dash_cooldown_reduced = (
            self.power_up == "bold" and not self.no_dash_cooldown)
        self.dash_cooldown_remaining = (
            0.0 if self.no_dash_cooldown else self.DASH_COOLDOWN
            * (1 - self.BOLD_EFFECT / 100
               if self._dash_cooldown_reduced else 1))
        self.renderer.dash_active = True
        self.renderer.dash_trail = []

    def _end_dash(self) -> None:
        self.dash_remaining = 0.0
        self.renderer.dash_active = False
        self.renderer.dash_trail = []

    def _advance_dash_cooldown(self, dt: float) -> None:
        self.dash_cooldown_remaining = max(
            0.0, self.dash_cooldown_remaining - dt)
        if self.dash_cooldown_remaining < 1e-9:
            self.dash_cooldown_remaining = 0.0

    def _record_dash_position(self, position: tuple[float, float]) -> None:
        trail = self.renderer.dash_trail
        if not trail or hypot(position[0] - trail[-1][0],
                              position[1] - trail[-1][1]) >= 0.3:
            trail.append(position)
            del trail[:-6]

    def _item_spawn_position(self) -> tuple[int, int]:
        game_map = self.renderer.map
        reachable = reachable_cells(game_map.maze, game_map.pacman.cell)
        candidates = reachable[1:] or reachable
        occupied = {fruit.position for fruit in game_map.extra_fruits}
        occupied.update(item.position for item in game_map.power_ups)
        if game_map.fruit is not None:
            occupied.add(game_map.fruit.position)
        available = [position for position in candidates
                     if position not in occupied]
        return random.choice(available or candidates)

    def _new_fruit(self, name: str) -> Fruit:
        return Fruit(name, self.renderer.map.maze, self.FRUIT_SPEED,
                     position=self._item_spawn_position())

    def spawn_random_power_up(self) -> None:
        """Add a power-up using the usual weighted selection."""
        names = tuple(POWER_UP_PROBS)
        name = random.choices(names, weights=tuple(POWER_UP_PROBS.values()),
                              k=1)[0]
        self.renderer.map.power_ups.append(
            PowerUp(name, self.renderer.map.maze, self.FRUIT_SPEED,
                    position=self._item_spawn_position()))

    def _spawn_fruit(self) -> None:
        game_map = self.renderer.map
        level = min(self.current_level, max(FRUIT_LEVELS.values()))
        name = next(name for name, fruit_level in FRUIT_LEVELS.items()
                    if fruit_level == level)
        game_map.fruit = self._new_fruit(name)
        self._fruit_spawned = True

    def spawn_random_fruit(self) -> None:
        """Add a bonus fruit without affecting the level's normal spawn."""
        name = random.choice(tuple(FRUIT_LEVELS))
        self.renderer.map.extra_fruits.append(self._new_fruit(name))

    def _advance_pickup(self, item: Fruit, dt: float) -> None:
        old_age = item.age
        item.age = min(self.FRUIT_LIFETIME, item.age + dt)
        landing = RenderMap._bounce_duration()
        moving_time = max(0.0, item.age - max(old_age, landing))
        if item.moving and moving_time:
            item.behaviour(moving_time)

    def _update_fruit(self, dt: float) -> None:
        game_map = self.renderer.map
        fruits = ([game_map.fruit] if game_map.fruit is not None else [])
        fruits.extend(game_map.extra_fruits)
        for fruit in fruits:
            self._advance_pickup(fruit, dt)
            if fruit.age >= self.FRUIT_LIFETIME - 1e-9:
                if fruit is game_map.fruit:
                    game_map.fruit = None
                else:
                    game_map.extra_fruits.remove(fruit)

    def _update_power_ups(self, dt: float) -> None:
        game_map = self.renderer.map
        for item in game_map.power_ups[:]:
            self._advance_pickup(item, dt)
            if item.age >= self.FRUIT_LIFETIME - 1e-9:
                game_map.power_ups.remove(item)
        if self.power_up_left is not None:
            self.power_up_left = max(0.0, self.power_up_left - dt)
            if self.power_up_left < 1e-9:
                self.clear_power_up()

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
        if (not self.renderer.game_init or self.renderer.revealing
                or self.game_over):
            return
        if not self.time_up:
            self.time_left = max(0.0, self.time_left - dt)
            self.time_up = self.time_left == 0.0

        self._cooldown_frame_remaining = dt
        self._update_movement(dt)
        self._advance_dash_cooldown(self._cooldown_frame_remaining)
        self._cooldown_frame_remaining = 0.0

    def _update_movement(self, dt: float) -> None:
        if self._check_collisions() or self.life_lost:
            return
        dash_time = min(dt, self.dash_remaining)
        if dash_time > 0:
            completed = self._move(dash_time, dashing=True)
            self.dash_remaining = max(0.0, self.dash_remaining - dash_time)
            if self.dash_remaining < 1e-9:
                self._end_dash()
                if not completed and (self._check_collisions()
                                      or self.life_lost):
                    return
            if self.life_lost or completed:
                return
        if dt > dash_time:
            self._move(dt - dash_time, dashing=False)

    def _move(self, dt: float, dashing: bool) -> bool:
        game_map = self.renderer.map
        base_factor = (self.FLASH_MODE_SPEED if self.flash_mode else 1.0)
        if dashing:
            base_factor *= self.DASH_SPEED
        coffee_possible = (self.power_up == "coffee"
                           or any(item.name == "coffee"
                                  for item in game_map.power_ups))
        behelit_possible = (self.power_up == "behelit"
                            or any(item.name == "behelit"
                                   for item in game_map.power_ups))
        max_speed = max([game_map.pacman.speed * base_factor
                         * (self.COFFEE_EFFECT if coffee_possible else 1.0),
                         self.FRUIT_SPEED]
                        + [ghost.speed * (self.BEHELIT_EFFECT
                                          if behelit_possible else 1)
                           for ghost in game_map.ghosts])
        steps = max(1, ceil(max_speed * dt / 0.1))
        step_dt = dt / steps
        for _ in range(steps):
            remaining = step_dt
            while remaining > 1e-12:
                segment = remaining
                if self.power_up_left is not None:
                    segment = min(segment, self.power_up_left)
                self._advance_dash_cooldown(segment)
                self._cooldown_frame_remaining = max(
                    0.0, self._cooldown_frame_remaining - segment)
                pacman_factor = base_factor
                if self.power_up == "coffee":
                    pacman_factor *= self.COFFEE_EFFECT
                elif self.power_up == "horror":
                    pacman_factor *= self.HORROR_EFFECT
                for ghost in game_map.ghosts:
                    ghost.behaviour(segment, game_map.pacman)
                self._update_fruit(segment)
                if dashing:
                    self._record_dash_position(game_map.pacman.position)
                game_map.pacman.update_position(
                    segment, game_map.maze, speed_multiplier=pacman_factor)
                self._update_power_ups(segment)
                if self._check_collisions():
                    return True
                if self.life_lost:
                    return False
                remaining -= segment
        return False

    def _check_collisions(self) -> bool:
        game_map = self.renderer.map
        contacts = self.collisions.check(
            game_map.pacman,
            [] if (self.invincible or self.dash_remaining > 0
                   or self.power_up == "star")
            else game_map.ghosts,
            game_map.pacgums,
            game_map.super_pacgums)
        for gum in contacts.pacgums:
            gum.eaten = True
            self.add_points(self.points_per_pacgum)
            self.pacgums_eaten += 1
            if (self.pacgums_eaten % self.POWER_UP_INTERVAL == 0
                    and random.random() < self.POWER_UP_CHANCE):
                self.spawn_random_power_up()
        for item in game_map.power_ups[:]:
            if (item.age >= RenderMap._bounce_duration()
                    and hypot(game_map.pacman.position[0] - item.map_pos[0],
                              game_map.pacman.position[1] - item.map_pos[1])
                    <= self.collisions.GHOST_DISTANCE):
                self.activate_power_up(item.name)
                game_map.power_ups.remove(item)
        for sup in contacts.super_pacgums:
            sup.eaten = True
            self.add_points(self.points_per_super_pacgum)
            game_map.pacman.size = 1.2
            for ghost in game_map.ghosts:
                if ghost.state not in (State.EATEN, State.WAITING):
                    ghost.state = State.FRIGHTENED
                    ghost.frightened_time = self.FRIGHTENED_TIME * (
                        self.GOLD_DONUT_EFFECT if self.gold_donut_active else 1.0)
        fruits = ([game_map.fruit] if game_map.fruit is not None else [])
        fruits.extend(game_map.extra_fruits)
        for fruit in fruits:
            if (fruit.age >= RenderMap._bounce_duration()
                    and hypot(game_map.pacman.position[0] - fruit.map_pos[0],
                              game_map.pacman.position[1] - fruit.map_pos[1])
                    <= self.collisions.GHOST_DISTANCE):
                fruit.eaten = True
                self.collect_fruit(fruit.value)
                if fruit is game_map.fruit:
                    game_map.fruit = None
                else:
                    game_map.extra_fruits.remove(fruit)

        if (not self._fruit_spawned and game_map.pacgums
                and sum(gum.eaten for gum in game_map.pacgums) * 2
                > len(game_map.pacgums)):
            self._spawn_fruit()

        # --  Ghosts States Updating  -------------------------------
        pacgums = game_map.pacgums
        total_left = sum(
            1 for pacgum in pacgums if not getattr(pacgum, "eaten", None) == False)

        #if total_left < 20:
        #    game_map.fruits
        for ghost in game_map.ghosts:
            if self.time_up:
                ghost.state = State.NIGHTMARE
                continue
            if ghost == Blinky and total_left < 10:
                Blinky.fury = True
                if total_left < 5:
                    Blinky.speed = 1.1
                else:
                    Blinky.speed = 1

        for ghost in contacts.ghosts:
            if ghost.state == State.FRIGHTENED:
                ghost.start_respawn(self.RESPAWN_TIME)
                self.add_points(self.points_per_ghost)
            elif ghost.state in (State.EATEN, State.WAITING):
                continue
            elif self.power_up == "star":
                continue
            else:
                self.lose_life()
                self.life_lost = True
        return bool(contacts.pacgums or contacts.super_pacgums) \
            and self.level_complete

    def reset_positions(self) -> None:
        self._end_dash()
        game_map = self.renderer.map
        game_map.pacman.reset_position()
        for ghost in game_map.ghosts:
            ghost.reset_position()
            ghost.state = ghost._default_state
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
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    if (not self.renderer.revealing and not self.game_over
                            and not getattr(event, "repeat", False)):
                        self._start_dash()
                    return True
                elif event.key in (pygame.K_w, pygame.K_UP):
                    pacman.wanted = 0
                    return True
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    pacman.wanted = 1
                    return True
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    pacman.wanted = 2
                    return True
                elif event.key in (pygame.K_a, pygame.K_LEFT):
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