from __future__ import annotations
import pygame
import colorsys
from typing import Any
from graphics.sprite_utils import change_color, get_tinted_image, tint_surface, resize

#class Map(MazeGenerator):
#    def __init__(self, size: tuple[int, int], pacgum: int, seed: int, ghosts: list[BaseGhost], max_time: int):
#        super().__init__(size, seed)
#        self.pacman: PacMan = PacMan(tuple(el // 2 for el in size))
#        self.ghosts: list[Ghost] = GhostFactory().create([g.model_dump() for g in ghosts])
#        self.pacgums: list[PacGum] = PacGumFactory.create(self.maze, pacgum)
#        self.max_time: int = max_time


class RenderMap:
    """ Render the map on the screen

    1. Remove color from tiles -> Remove color using change_color().
    2. Draw tiles and pacman from the corner top-left to the corner bottom-right.
    3. Restore color in tiles from the corner top-left to the corner bottom-right.
    4. Add pacgums into the map.
    5. Add ghosts to the map.
    """

    MAP_FOLDER = "maps"
    SPRITE_FOLDER = "sprites"
    BACKGROUND = (0, 0, 0)

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
        "pac-dots": 0.4,
        "power-pellets": 0.7,
        "fruit": 0.7,
        "power-up": 0.7,
    }

    def __init__(self, game_map: Any, assets: Any, size: tuple[int, int],
                 origin: tuple[int, int] = (0, 0)) -> None:
        maze = game_map.maze
        self._validate(maze)
        self.map = game_map
        self.assets = assets
        self.rows = len(maze)
        self.cols = len(maze[0])

        self.tile = max(1, min(size[0] // self.cols, size[1] // self.rows))
        width, height = self.cols * self.tile, self.rows * self.tile
        self.origin = (origin[0] + (size[0] - width) // 2,
                       origin[1] + (size[1] - height) // 2)

        self._tiles_color: dict[int, pygame.Surface] = {}
        self._tiles_gray: dict[int, pygame.Surface] = {}
        self._bg_color: pygame.Surface | None = None
        self._bg_gray: pygame.Surface | None = None
        self._sprites: dict[tuple[str, float], pygame.Surface] = {}

        self.revealing = False
        self._reveal_surface: pygame.Surface | None = None
        self._reveal_time = 0.0
        self._reveal_duration = 1.0
        self._reveal_diagonal = -1

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

    def load_map(self) -> None:
        """
        Prepare the static maze surfaces (colored and grayscale).

        Only the tile values that appear in the maze are loaded. Called
        automatically by `draw` if needed; call it earlier (for example
        while a loading screen is shown) to avoid a pause on first draw.
        """
        maze = self.map.maze
        for value in {v for row in maze for v in row}:
            image = self.assets.get_image(
                f"{self.MAP_FOLDER}/{value}", (self.tile, self.tile),
                group="map")
            self._tiles_color[value] = image
            self._tiles_gray[value] = tint_surface(image, saturation=0.0)

        self._bg_color = self._compose(self._tiles_color)
        self._bg_gray = self._compose(self._tiles_gray)

    def _compose(self, tiles: dict[int, pygame.Surface]) -> pygame.Surface:
        """Blit every tile once into one opaque surface."""
        surface = pygame.Surface((self.cols * self.tile,
                                  self.rows * self.tile))
        surface.fill(self.BACKGROUND)
        for row, values in enumerate(self.map.maze):
            for col, value in enumerate(values):
                surface.blit(tiles[value],
                             (col * self.tile, row * self.tile))
        return surface

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the map and everything on it.

        Parameters
        ----------
        screen : pygame.Surface
            Surface to draw on.
        """
        if self._bg_color is None:
            self.load_map()

        if self.revealing:
            screen.blit(self._reveal_surface, self.origin)
            self._draw_pacman(screen)
        else:
            screen.blit(self._bg_color, self.origin)
            self._draw_pacgums(screen)
            self._draw_pacman(screen)
            self._draw_ghosts(screen)

    # ----  Intro animation  -------------------------------------------
    def start_reveal(self, duration: float = 1.5) -> None:
        """
        Start the grayscale-to-color intro animation.

        Parameters
        ----------
        duration : float, optional
            Seconds the color takes to sweep from the top-left corner to
            the bottom-right corner. Default is ``1.5``.
        """
        if self._bg_gray is None:
            self.load_map()
        self._reveal_surface = self._bg_gray.copy()
        self._reveal_time = 0.0
        self._reveal_duration = max(duration, 1e-6)
        self._reveal_diagonal = -1
        self.revealing = True

    def finish_reveal(self) -> None:
        """Skip the intro animation."""
        self.revealing = False
        self._reveal_surface = None

    def update(self, dt: float) -> None:
        """
        Advance the intro animation.

        Parameters
        ----------
        dt : float
            Seconds since the previous frame.
        """
        if not self.revealing:
            return
        self._reveal_time += dt
        progress = min(1.0, self._reveal_time / self._reveal_duration)
        diagonals = self.rows + self.cols - 1
        target = int(progress * diagonals) - 1

        # Restore color one anti-diagonal at a time (row + col == d).
        for d in range(self._reveal_diagonal + 1, target + 1):
            for row in range(max(0, d - self.cols + 1),
                             min(self.rows, d + 1)):
                col = d - row
                rect = pygame.Rect(col * self.tile, row * self.tile,
                                   self.tile, self.tile)
                self._reveal_surface.fill(self.BACKGROUND, rect)
                self._reveal_surface.blit(
                    self._tiles_color[self.map.maze[row][col]], rect)
        self._reveal_diagonal = max(self._reveal_diagonal, target)

        if progress >= 1.0:
            self.finish_reveal()

    # ----  Drawing  ---------------------------------------------------
    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the map and everything on it.

        Parameters
        ----------
        screen : pygame.Surface
            Surface to draw on.
        """
        if self._bg_color is None:
            self.load_map()

        if self.revealing:
            screen.blit(self._reveal_surface, self.origin)
            self._draw_pacman(screen)
        else:
            screen.blit(self._bg_color, self.origin)
            self._draw_pacgums(screen)
            self._draw_pacman(screen)
            self._draw_ghosts(screen)

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
            if getattr(ghost, "frightened", False):
                sprite = self._sprite(self.FRIGHTENED_SPRITE)
            else:
                sprite = self._sprite(self.GHOST_SPRITE,
                                      getattr(ghost, "hue", 0.0))
            self._blit(screen, sprite, getattr(ghost, "position", ghost))

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

    def _blit(self, screen: pygame.Surface, image: pygame.Surface,
              position: tuple[float, float]) -> None:
        """Draw `image` centered on the cell at `position` (col, row)."""
        x, y = position
        center = (round(self.origin[0] + (x + 0.5) * self.tile),
                  round(self.origin[1] + (y + 0.5) * self.tile))
        screen.blit(image, image.get_rect(center=center))
 