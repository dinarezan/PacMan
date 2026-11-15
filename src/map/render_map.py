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

    def __init__(self, map, assets, size: tuple[int, int]):
        self.map = map
        self.assets = assets
        self.size = size

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

    def add_tiles_map(self) -> None:
        """ Load the tiles in the screen 
        
        Use images from assets/map/
        each image have a name from 0 to 15
        Use each image for each value in map.maze
        """
        print("level:\n", map.maze)

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
 

    

