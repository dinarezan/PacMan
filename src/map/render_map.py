from __future__ import annotations
import pygame
import colorsys
import random
from typing import Any
from src.graphics.sprite_utils import change_color, get_tinted_image, tint_surface, resize
from src.entities.map import Map

#class Map(MazeGenerator):
#    def __init__(self, size: tuple[int, int], pacgum: int, seed: int, ghosts: list[BaseGhost], max_time: int):
#        super().__init__(size, seed)
#        self.pacman: PacMan = PacMan(tuple(el // 2 for el in size))
#        self.ghosts: list[Ghost] = GhostFactory().create([g.model_dump() for g in ghosts])
#        self.pacgums: list[PacGum] = PacGumFactory.create(self.maze, pacgum)
#        self.max_time: int = max_time


class RenderMap:
    """
    Render the map on the screen.

    The maze tiles never change, so they are composed once into a single
    surface and blitted with one call per frame. Collectibles, Pac-Man and
    the ghosts are drawn on top every frame, at their current positions.

    Draw order: tiles, pacgums, Pac-Man, ghosts.

    An optional intro animation (`start_reveal`) first shows the maze and
    Pac-Man in grayscale, then restores the color from the top-left
    corner to the bottom-right corner; pacgums and ghosts appear when it
    ends.

    Parameters
    ----------
    game_map : object
        Provides ``maze``: a tuple of tuples of ints in ``0..15``,
        indexed ``maze[row][column]``. It may also provide (all
        optional, read every frame):

        - ``pacman``: has ``position``.
        - ``pacgums``: iterable of items with ``position`` and an
          optional ``kind`` (``"dot"``, ``"power"``, ``"fruit"``,
          ``"power-up"``, or any file name in ``assets/sprites``).
        - ``ghosts``: iterable of items with ``position`` and optional
          ``frightened`` (bool) and ``hue`` (degrees, to color-shift the
          ghost sprite).

        A ``position`` is ``(column, row)`` in cell units and may be a
        float for smooth movement. A plain ``(column, row)`` tuple is
        accepted in place of an object.
    assets : AssetManager
        Provides ``get_image(name, scale, group=...)``. Tiles are read
        from ``map/<value>`` and sprites from ``sprites/<name>``.
    size : tuple of int
        Pixel area ``(width, height)`` available for the map. The tile
        size is the largest that fits and the map is centered in it.
    origin : tuple of int, optional
        Top-left corner of that area on the screen. Default ``(0, 0)``.

    Attributes
    ----------
    rows, cols : int
        Maze dimensions in tiles.
    tile : int
        Tile size in pixels.
    origin : tuple of int
        Top-left pixel of the (centered) maze on the screen.
    revealing : bool
        True while the intro animation is running.

    Raises
    ------
    ValueError
        If the maze is empty, ragged, or has values outside ``0..15``.
    """
    # ? Moved to another file with data.
    MAP_FOLDER = "maps"
    SPRITE_FOLDER = "sprites"
    BACKGROUND = (0, 0, 0)
    BG_IMAGE = "maps/bg"

    PACMAN_SPRITE = "pacman"
    GHOST_SPRITE = "ghost"
    FRIGHTENED_SPRITE = "frightered-ghost"   # matches the file name
    KIND_SPRITES = {
        "dot": "pac-dots",
        "power": "donut",
        "fruit": "cherry",
        "power-up": "coffee",
    }

    #    "dot": "pac-dots",
    #    "power": "power-pellets",
    #    "fruit": "fruit",
    #    "power-up": "power-up",
    # Sprite size relative to a tile (collectibles are smaller).
    SPRITE_SCALE = {
        "pac-dots": 1,
        "power-pellets": 1,
        "fruit": 1,
        "power-up": 1,
    }


# -- animation tuning (seconds unless noted) -----------------------
    SOFT_DIAGONALS = 3        # width of the tile fade-in front, in tiles
    BLOB_SPACING = 0.6        # color blobs lattice spacing, in tiles
    BLOB_JITTER = 0.2         # random blob displacement, in spacings
    BLOB_GROW = 0.3           # blob growth time, fraction of color_time
    DROP_TILES = 2.0          # height pacgums and ghosts fall from
    DOT_FALL_TIME = 0.35      # first fall of a pacgum
    DOT_RESTITUTION = 0.45    # bounce height ratio (0 = no rebound)
    DOT_BOUNCES = 3
    DOT_WAVE_TIME = 0.8       # TL -> BR spread of the pacgum drops
    DOT_JITTER = 0.15         # random extra delay per pacgum
    GHOST_FALL_TIME = 0.5
    GHOST_STAGGER = 0.2       # delay between ghosts
    GHOST_START_SCALE = 0.2
    SHADOW_WIDTH = 0.8        # shadow width relative to the sprite
    SHADOW_OFFSET = 0.3       # shadow drop below center, times sprite height
    SHADOW_LAYERS = 16

    def __init__(self, game_map: Map, assets: Any, size: tuple[int, int],
                 origin: tuple[int, int] = (0, 0),
                 screen_size: tuple[int, int] | None = None) -> None:
        maze = game_map.maze
        self._validate(maze)
        self.map = game_map
        self.assets = assets
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.screen_size = screen_size

        self.tile = max(1, min(size[0] // self.cols, size[1] // self.rows))
        self.map_size = (self.cols * self.tile, self.rows * self.tile)
        self.origin = (origin[0] + (size[0] - self.map_size[0]) // 2,
                       origin[1] + (size[1] - self.map_size[1]) // 2)

        self._tiles_color: dict[int, pygame.Surface] = {}
        self._tiles_gray: dict[int, pygame.Surface] = {}
        self._color_map: pygame.Surface | None = None   # maze, RGBA
        self._bg_screen: pygame.Surface | None = None   # bg tiles only
        self._static: pygame.Surface | None = None      # bg + maze
        self._sprites: dict[tuple[str, float], pygame.Surface] = {}
        self._shadows: dict[tuple[int, int], pygame.Surface] = {}

        self.revealing = False
        self._time = 0.0
        self.game_init = False
        self._reset_intro()

    @staticmethod
    def _validate(maze: Any) -> None:
        if not maze or not maze[0]:
            raise ValueError("The maze is empty")
        width = len(maze[0])
        for row in maze:
            if len(row) != width:
                raise ValueError("All maze rows must have the same length")
            for value in row:
                if not 0 <= value <= 15:
                    raise ValueError(
                        f"Tile value {value} is outside 0..15")

    # --  Loading  -----------------------------------------------------
    def load_map(self) -> None:
        """
        Prepare the static surfaces (background, colored maze) -> Load assets.

        Only the tile values that appear in the maze are loaded. Called
        automatically by `draw` and `start_reveal` if needed; To use along
        loading screen to improve performance.
        """
        for value in {v for row in self.map.maze for v in row}:
            image = self.assets.get_image(
                f"{self.MAP_FOLDER}/{value}", (self.tile, self.tile),
                group="map")
            self._tiles_color[value] = image
            self._tiles_gray[value] = tint_surface(image, saturation=0.0)

        self._color_map = pygame.Surface(self.map_size, pygame.SRCALPHA)
        for row, values in enumerate(self.map.maze):
            for col, value in enumerate(values):
                self._color_map.blit(self._tiles_color[value],
                                     (col * self.tile, row * self.tile))

        self._bg_screen = self._build_background()
        self._static = self._bg_screen.copy()
        self._static.blit(self._color_map, self.origin)

    def _build_background(self) -> pygame.Surface:
        """Fill the whole screen with the background tile, grid-aligned."""
        if self.screen_size is not None:
            width, height = self.screen_size
        else:
            display = pygame.display.get_surface()
            width, height = (display.get_size() if display else
                             (self.origin[0] * 2 + self.map_size[0],
                              self.origin[1] * 2 + self.map_size[1]))
        surface = pygame.Surface((width, height))
        surface.fill(self.BACKGROUND)
        image = self.assets.get_image(
            self.BG_IMAGE, (self.tile, self.tile), group="map")
        # Start before the screen edge so tiles line up with the maze grid.
        x0 = self.origin[0] % self.tile - self.tile
        y0 = self.origin[1] % self.tile - self.tile
        for y in range(y0, height, self.tile):
            for x in range(x0, width, self.tile):
                surface.blit(image, (x, y))
        return surface

    # --  Intro animation  ---------------------------------------------
    def _reset_intro(self) -> None:
        self._draw_time = 1.0
        self._color_time = 1.0
        self._gray_layer: pygame.Surface | None = None
        self._gray_done = 0
        self._mask: pygame.Surface | None = None
        self._colored: pygame.Surface | None = None
        self._blobs: list[tuple[float, int, int, float]] = []
        self._blob_next = 0
        self._active_blobs: list[tuple[float, int, int, float]] = []
        self._dots: list[tuple[str, Any, float]] = []
        self._ghosts: list[tuple[Any, Any, float]] = []
        self._pacman: Any = None
        self._pacman_time = 0.0
        self._t_dots = self._t_ghosts = self._t_end = 0.0

    def start_reveal(self, draw_time: float = 1.2,
                     color_time: float = 1.2) -> None:
        """
        Start the intro animation.

        Parameters
        ----------
        draw_time : float, optional
            Seconds the gray maze takes to be drawn from the top-left to
            the bottom-right corner. Default is ``1.2``.
        color_time : float, optional
            Seconds the color takes to spread over the maze. Default is
            ``1.2``. Pacgums and ghosts then fall, using the
            ``DOT_*`` and ``GHOST_*`` class constants for timing.
        """
        if self._static is None:
            self.load_map()
        rng = random.Random(0)          # same intro on every run
        self._reset_intro()
        self._time = 0.0
        self._draw_time = max(draw_time, 1e-6)
        self._color_time = max(color_time, 1e-6)
        self._gray_layer = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self._mask = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self._blobs = self._make_blobs(rng)
        self._plan_drops(rng)
        self.revealing = True

    def finish_reveal(self) -> None:
        """Skip to the end of the intro animation."""
        self.revealing = False
        self._reset_intro()

    def _make_blobs(self, rng: random.Random
                    ) -> list[tuple[float, int, int, float]]:
        """
        Make the color blobs ``(start, x, y, radius)``, sorted by start.

        Blobs sit on a jittered lattice; later start times belong to
        blobs further from the top-left corner, with some randomness.
        """
        width, height = self.map_size
        step = max(2.0, self.tile * self.BLOB_SPACING)
        latest = self._color_time * (1.0 - self.BLOB_GROW)
        blobs = []
        y = 0.0
        while y < height + step:
            x = 0.0
            while x < width + step:
                cx = x + rng.uniform(-1, 1) * step * self.BLOB_JITTER
                cy = y + rng.uniform(-1, 1) * step * self.BLOB_JITTER
                along = (cx / width + cy / height) / 2
                start = along * latest + rng.uniform(
                    0, 0.1 * self._color_time)
                start = max(0.0, min(latest, start))
                radius = step * rng.uniform(1.1, 1.4)
                blobs.append((start, round(cx), round(cy), radius))
                x += step
            y += step
        blobs.sort()
        return blobs

    def _plan_drops(self, rng: random.Random) -> None:
        """Read pacgums/ghosts/Pac-Man and schedule the intro timeline."""
        span = max(1, self.rows + self.cols - 2)
        for item in getattr(self.map, "pacgums", ()):
            x, y = getattr(item, "position", item)
            name = self.KIND_SPRITES.get(getattr(item, "kind", "dot"),
                                         getattr(item, "kind", "dot"))
            wave = max(0.0, min(1.0, (x + y) / span))
            delay = wave * self.DOT_WAVE_TIME + rng.uniform(
                0, self.DOT_JITTER)
            self._dots.append((name, (x, y), delay))
        for index, ghost in enumerate(getattr(self.map, "ghosts", ())):
            self._ghosts.append((ghost, getattr(ghost, "position", ghost),
                                 index * self.GHOST_STAGGER))

        pacman = getattr(self.map, "pacman", None)
        if pacman is not None:
            self._pacman = pacman
            x, y = getattr(pacman, "position", pacman)
            diagonals = self.rows + self.cols - 1
            diagonal = min(diagonals - 1, int(x) + int(y))
            soft = self.SOFT_DIAGONALS
            # Time at which the Pac-Man tile is fully drawn.
            self._pacman_time = (self._draw_time * (diagonal + soft)
                                 / (diagonals + soft))

        t = self._draw_time + self._color_time
        self._t_dots = t
        if self._dots:
            t += (self.DOT_WAVE_TIME + self.DOT_JITTER
                  + self._bounce_duration())
        self._t_ghosts = t
        if self._ghosts:
            t += (self.GHOST_STAGGER * (len(self._ghosts) - 1)
                  + self.GHOST_FALL_TIME)
        self._t_end = t

    # -- falling physics -----------------------------------------------
    def _bounce_duration(self) -> float:
        """Total time of a pacgum drop, including all rebounds."""
        e = self.DOT_RESTITUTION
        return self.DOT_FALL_TIME * (
            1 + 2 * sum(e ** k for k in range(1, self.DOT_BOUNCES + 1)))

    def _bounce(self, t: float, drop: float) -> float:
        """Height in pixels above the ground `t` seconds after release."""
        if t <= 0:
            return drop
        g = 2 * drop / self.DOT_FALL_TIME ** 2
        if t < self.DOT_FALL_TIME:
            return drop - 0.5 * g * t * t
        t -= self.DOT_FALL_TIME
        speed = g * self.DOT_FALL_TIME * self.DOT_RESTITUTION
        for _ in range(self.DOT_BOUNCES):
            flight = 2 * speed / g
            if t < flight:
                return speed * t - 0.5 * g * t * t
            t -= flight
            speed *= self.DOT_RESTITUTION
        return 0.0

    # ---- per-frame update --------------------------------------------
    def update(self, dt: float) -> None:
        """
        Advance the intro animation. When ends, activate the playing mode.

        Parameters
        ----------
        dt : float
            Seconds since the previous frame.
        """
        if not self.revealing:
            return
        self._time += dt
        self._update_gray()
        if self._time >= self._draw_time:
            self._update_color(self._time - self._draw_time)
        if self._time >= self._t_end:
            self.finish_reveal()
        if not self.game_init:
            self.game_init = True

    def _update_gray(self) -> None:
        """Fade in the gray tiles along anti-diagonals (row + col = d)."""
        diagonals = self.rows + self.cols - 1
        if self._gray_done >= diagonals:
            return
        soft = self.SOFT_DIAGONALS
        progress = min(1.0, self._time / self._draw_time)
        wave = progress * (diagonals + soft)
        last = min(diagonals - 1, int(wave))
        layer, tile = self._gray_layer, self.tile

        for d in range(self._gray_done, last + 1):
            alpha = min(1.0, (wave - d) / soft)
            for row in range(max(0, d - self.cols + 1),
                             min(self.rows, d + 1)):
                col = d - row
                image = self._tiles_gray[self.map.maze[row][col]]
                rect = pygame.Rect(col * tile, row * tile, tile, tile)
                layer.fill((0, 0, 0, 0), rect)
                if alpha < 1.0:
                    image.set_alpha(int(alpha * 255))
                    layer.blit(image, rect)
                    image.set_alpha(255)
                else:
                    layer.blit(image, rect)
        self._gray_done = max(self._gray_done,
                              min(diagonals, int(wave - soft) + 1))

    def _update_color(self, t: float) -> None:
        """Grow the color blobs and rebuild the masked color layer."""
        grow = self.BLOB_GROW * self._color_time
        blobs = self._blobs
        while (self._blob_next < len(blobs)
               and blobs[self._blob_next][0] <= t):
            self._active_blobs.append(blobs[self._blob_next])
            self._blob_next += 1

        still_growing = []
        for blob in self._active_blobs:
            start, cx, cy, radius = blob
            u = (t - start) / grow
            if u >= 1.0:
                current = radius
            else:
                current = radius * (1 - (1 - u) ** 2)      # ease-out
                still_growing.append(blob)
            if current >= 1:
                pygame.draw.circle(self._mask, (255, 255, 255, 255),
                                   (cx, cy), int(current))
        self._active_blobs = still_growing

        if t < self._color_time:
            # Keep the color only where the mask has been painted.
            colored = self._color_map.copy()
            colored.blit(self._mask, (0, 0),
                         special_flags=pygame.BLEND_RGBA_MULT)
            self._colored = colored

    # ----  Drawing  ---------------------------------------------------
    def draw(self, screen: pygame.Surface, dt: float) -> None:
        """
        Draw the map and everything on it.

        Parameters
        ----------
        screen : pygame.Surface
            Surface to draw on.
        """
        if self._static is None:
            self.load_map()
        if self.revealing:
            self._draw_intro(screen)
            return

        screen.blit(self._static, (0, 0))
        self._draw_shadows(screen)
        self._draw_pacgums(screen)
        self._draw_pacman(screen)
        self._draw_ghosts(screen)
        pacman = self.map.pacman
        for ghost in self.map.ghosts:
            ghost.behaviour(dt, pacman)
        if self.game_init:
            pacman.update_position(dt, self.map.maze)


    def _draw_intro(self, screen: pygame.Surface) -> None:
        """Draw one frame of the intro animation."""
        t = self._time
        if t >= self._draw_time + self._color_time:
            screen.blit(self._static, (0, 0))
        else:
            screen.blit(self._bg_screen, (0, 0))
            screen.blit(self._gray_layer, self.origin)
            if self._colored is not None:
                screen.blit(self._colored, self.origin)

        pacman = getattr(self.map, "pacman", ())
        self._draw_shadow(screen, getattr(pacman, "position", pacman),
                          self._sprite(self.PACMAN_SPRITE), strength=1.0,
                          size=(50, 70))
        self._draw_shadow(screen, getattr(pacman, "position", pacman),
                          self._sprite(self.PACMAN_SPRITE), strength=1.0,
                          size=(50, 70))

        drop = self.DROP_TILES * self.tile

        dots = []
        for name, position, delay in self._dots:
            elapsed = t - self._t_dots - delay
            if elapsed < 0:
                continue
            height = self._bounce(elapsed, drop)
            sprite = self._sprite(name)
            self._draw_shadow(screen, position, sprite,
                              1.0 - min(height / drop, 0.7))
            dots.append((sprite, position, height))

        ghosts = []
        for ghost, position, delay in self._ghosts:
            elapsed = t - self._t_ghosts - delay
            if elapsed < 0:
                continue
            u = min(elapsed / self.GHOST_FALL_TIME, 1.0)
            height = drop * (1.0 - u * u)           # accelerating fall
            scale = (self.GHOST_START_SCALE
                     + (1.0 - self.GHOST_START_SCALE) * u)
            sprite = self._scaled(self._ghost_sprite(ghost), scale)
            self._draw_shadow(screen, position, sprite, u * u)
            ghosts.append((sprite, position, height))

        for sprite, position, height in dots:
            self._blit(screen, sprite, position, lift=height)
        if self._pacman is not None and t >= self._pacman_time:
            self._draw_pacman(screen)
        for sprite, position, height in ghosts:
            self._blit(screen, sprite, position, lift=height)

    # ! ADD here new shadow on other elements
    def _draw_shadows(self, screen: pygame.Surface) -> None:
        """Draw the resting shadow of every pacgum and ghost."""
        for item in getattr(self.map, "pacgums", ()):
            kind = getattr(item, "kind", "dot")
            sprite = self._sprite(self.KIND_SPRITES.get(kind, kind))
            self._draw_shadow(screen, getattr(item, "position", item),
                              sprite, strength=0.7)
        for ghost in getattr(self.map, "ghosts", ()):
            self._draw_shadow(screen, getattr(ghost, "position", ghost),
                              self._ghost_sprite(ghost))

        pacman = getattr(self.map, "pacman", ())
        self._draw_shadow(screen, getattr(pacman, "position", pacman),
                          self._sprite(self.PACMAN_SPRITE), strength=1.0,
                          size=(50, 70))
        self._draw_shadow(screen, getattr(pacman, "position", pacman),
                          self._sprite(self.PACMAN_SPRITE), strength=1.0,
                          size=(50, 70))

    def _draw_pacman(self, screen: pygame.Surface) -> None:
        """Draw Pac-Man."""
        pacman = getattr(self.map, "pacman", None)
        if pacman is not None:
            self._blit(screen, self._sprite(self.PACMAN_SPRITE),
                       getattr(pacman, "position", pacman))

    def _draw_pacgums(self, screen: pygame.Surface) -> None:
        """Draw dots, power pellets, fruit and power-ups."""
        for item in getattr(self.map, "pacgums", ()):
            kind = getattr(item, "kind", "dot")
            name = self.KIND_SPRITES.get(kind, kind)
            self._blit(screen, self._sprite(name),
                       getattr(item, "position", item))

    def _draw_ghosts(self, screen: pygame.Surface) -> None:
        """Draw the ghosts (blue when frightened)."""
        for ghost in getattr(self.map, "ghosts", ()):
            self._blit(screen, self._ghost_sprite(ghost),
                       getattr(ghost, "map_pos", ghost))

    # -- sprite helpers ------------------------------------------------
    def _ghost_sprite(self, ghost: Any) -> pygame.Surface:
        if getattr(ghost, "frightened", False):
            return self._sprite(self.FRIGHTENED_SPRITE)
        return self._sprite(self.GHOST_SPRITE, getattr(ghost, "hue", 0.0))

    def _sprite(self, name: str, hue: float = 0.0) -> pygame.Surface:
        """Return a sprite scaled for this map (cached; optional tint)."""
        key = (name, hue)
        sprite = self._sprites.get(key)
        if sprite is None:
            px = max(1, round(self.tile * self.SPRITE_SCALE.get(name, 1.0)))
            sprite = self.assets.get_image(
                f"{self.SPRITE_FOLDER}/{name}", (px, px), group="sprites")
            if hue:
                sprite = tint_surface(sprite, hue=hue)
            self._sprites[key] = sprite
        return sprite

    @staticmethod
    def _scaled(sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """Return `sprite` resized by `scale` (a no-op at full size)."""
        if scale >= 0.999:
            return sprite
        width, height = sprite.get_size()
        return pygame.transform.smoothscale(
            sprite, (max(1, round(width * scale)),
                     max(1, round(height * scale))))

    def _shadow(self, width: int, strength: float) -> pygame.Surface:
        """
        Return a soft ellipse shadow with a transparancy gradient (cached).

        `strength` in ``0..1`` makes it wider and darker.
        """
        step = int(max(0.0, min(1.0, strength)) * 10)
        key = (width, step)
        shadow = self._shadows.get(key)

        # Is in cache
        if shadow is not None:
            return shadow

        w = max(2, round(width * (0.5 + 0.05 * step)))
        h = max(1, round(w * 0.35))
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)

        max_alpha = 40 + 7 * step
        layers = self.SHADOW_LAYERS

        # Draw from the outside toward the center.
        for i in range(layers, 0, -1):
            progress = i / layers

            # Smaller ellipse as we move toward the center. # * Fake effect.
            rect = pygame.Rect(
                0,
                0,
                round(w * progress),
                round(h * progress),
            )
            rect.center = (w // 2, h // 2)

            # Quadratic curve gives a smoother falloff.
            alpha = round(max_alpha * (1.0 - progress) ** 2)

            pygame.draw.ellipse(
                shadow,
                (0, 0, 0, alpha),
                rect,
            )

        self._shadows[key] = shadow
        return shadow

    def _draw_shadow(self, screen: pygame.Surface, position: Any,
                     sprite: pygame.Surface, strength: float = 1.0,
                     size: tuple[int, int] | None = None) -> None:
        """Draw the ground shadow under the cell at `position`."""
        if size:
            width, height = size[0], size[1]
        else:
            width, height = sprite.get_size()
        shadow = self._shadow(round(width * self.SHADOW_WIDTH), strength)
        x, y = position
        center = (round(self.origin[0] + (x + 0.5) * self.tile),
                  round(self.origin[1] + (y + 0.5) * self.tile
                        + height * self.SHADOW_OFFSET))
        screen.blit(shadow, shadow.get_rect(center=center))

    def _blit(self, screen: pygame.Surface, image: pygame.Surface,
              position: Any, lift: float = 0.0) -> None:
        """Draw `image` centered on the cell at `position` (col, row).

        `lift` raises it by that many pixels (used for falling sprites).
        """
        x, y = position
        center = (round(self.origin[0] + (x + 0.5) * self.tile),
                  round(self.origin[1] + (y + 0.5) * self.tile - lift))
        screen.blit(image, image.get_rect(center=center))
