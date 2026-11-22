from __future__ import annotations

import math
from typing import Any

import pygame

from src.graphics.sprite_utils import tint_surface


class Hud:
    """
    Heads-up display: score and time on top; lives, bonus and fruits at
    the bottom.

    The HUD only draws. All the numbers come from a `Gameplay` object
    (``points``, ``time_left``, ``lives``, ``power_up``, ``fruits``).

    Parameters
    ----------
    assets : AssetManager
        Provides ``get_image(name, scale, group=...)``. Icons are read
        from the selected sprite set.

    Attributes
    ----------
    TOP_HEIGHT, BOTTOM_HEIGHT : int
        Height in pixels of the two bars. The map should be placed in
        the area between them (see ``Engine.start``).

    Layout
    ------
    Top:    ``SCORE 000120`` (left)                ``TIME 87`` (right)
    Bottom: Pac-Man icons, one per life (left)
            ``[dash]  [fruit] x3`` (right)
    """

    TOP_HEIGHT = 64
    BOTTOM_HEIGHT = 80
    MARGIN = 24
    GAP = 8
    ICON_SIZE = 50
    SPRITE_FOLDER = "sprites/low"
    LIVES_SPRITE = "heart"
    FRUIT_SPRITE = "cherry"
    DASH_SPRITE = "dash"

    PANEL_COLOR = (0, 0, 0, 150)
    TEXT_COLOR = (235, 235, 235)
    ALERT_COLOR = (255, 80, 80)
    BAR_BACK = (60, 60, 60)
    BAR_FRONT = (0, 220, 0)
    ALERT_SECONDS = 10          # time text turns red at or below this

    def __init__(self, assets: Any) -> None:
        self.assets = assets
        self.font = pygame.font.Font(None, 44)
        self._icons: dict[str, pygame.Surface] = {}
        self._dash_gray: pygame.Surface | None = None
        self._panels: dict[tuple[int, int], pygame.Surface] = {}

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, gameplay: Any) -> None:
        """
        Draw both bars.

        Parameters
        ----------
        screen : pygame.Surface
            Surface to draw on.
        gameplay : Gameplay
            Source of the numbers to show.
        """
        width, height = screen.get_size()
        self._draw_top(screen, gameplay, width)
        self._draw_bottom(screen, gameplay, width, height)

    def _draw_top(self, screen: pygame.Surface, gameplay: Any,
                  width: int) -> None:
        screen.blit(self._panel(width, self.TOP_HEIGHT), (0, 0))
        center_y = self.TOP_HEIGHT // 2

        score = self.font.render(f"SCORE  {gameplay.points:06d}", True,
                                 self.TEXT_COLOR)
        screen.blit(score, score.get_rect(
            midleft=(self.MARGIN, center_y)))

        seconds = math.ceil(gameplay.time_left)
        color = (self.ALERT_COLOR if seconds <= self.ALERT_SECONDS
                 else self.TEXT_COLOR)
        time_text = self.font.render(f"TIME  {seconds}", True, color)
        screen.blit(time_text, time_text.get_rect(
            midright=(width - self.MARGIN, center_y)))

    def _draw_bottom(self, screen: pygame.Surface, gameplay: Any,
                     width: int, height: int) -> None:
        top = height - self.BOTTOM_HEIGHT
        screen.blit(self._panel(width, self.BOTTOM_HEIGHT), (0, top))
        center_y = top + self.BOTTOM_HEIGHT // 2
        size = self.ICON_SIZE

        # Lives: one Pac-Man|heart icon per life, from the left.
        lives = self._icon(self.LIVES_SPRITE)
        count = max(0, min(gameplay.MAX_LIVES, gameplay.lives))
        for index in range(count):
            x = self.MARGIN + index * (size + self.GAP)
            screen.blit(lives, (x, center_y - size // 2))

        # Fruits eaten: "x3" at the right edge, icon to its left.
        x = width - self.MARGIN
        text = self.font.render(f"x{gameplay.fruits}", True,
                                self.TEXT_COLOR)
        x -= text.get_width()
        screen.blit(text, text.get_rect(midleft=(x, center_y)))
        x -= self.GAP + size
        screen.blit(self._icon(self.FRUIT_SPRITE),
                    (x, center_y - size // 2))
        x -= self.GAP + size
        dash = self._icon(self.DASH_SPRITE)
        if gameplay.dash_cooldown_remaining > 0:
            if self._dash_gray is None:
                self._dash_gray = tint_surface(dash, saturation=0.0)
            dash = self._dash_gray
        screen.blit(dash, (x, center_y - size // 2))

        # Active bonus ☕: to the left of the fruits, with remaining time.
        #if gameplay.power_up:
        #    x -= self.MARGIN + size
        #    screen.blit(self._icon(gameplay.power_up),
        #                (x, center_y - size // 2))
        #    self._draw_bonus_bar(screen, gameplay, x,
        #                         center_y + size // 2 + 3)

    def _draw_bonus_bar(self, screen: pygame.Surface, gameplay: Any,
                        x: int, y: int) -> None:
        """Thin bar under the bonus icon showing the time it has left."""
        if not gameplay.power_up_total:
            return
        #fraction = max(0.0, min(1.0, gameplay.power_up_left
        #                        / gameplay.power_up_total))
        fraction = max(0.0, min(1.0, 6.0))
        pygame.draw.rect(screen, self.BAR_BACK,
                         (x, y, self.ICON_SIZE, 5))
        pygame.draw.rect(screen, self.BAR_FRONT,
                         (x, y, round(self.ICON_SIZE * fraction), 5))

    # -- cached helpers ------------------------------------------------
    def _icon(self, name: str) -> pygame.Surface:
        """Return a cached ``ICON_SIZE`` square icon from the sprites."""
        icon = self._icons.get(name)
        if icon is None:
            icon = self.assets.get_image(
                f"{self.SPRITE_FOLDER}/{name}",
                (self.ICON_SIZE, self.ICON_SIZE), group="sprites")
            self._icons[name] = icon
        return icon

    def _panel(self, width: int, height: int) -> pygame.Surface:
        """Return a cached translucent dark bar background."""
        key = (width, height)
        panel = self._panels.get(key)
        if panel is None:
            panel = pygame.Surface(key, pygame.SRCALPHA)
            panel.fill(self.PANEL_COLOR)
            self._panels[key] = panel
        return panel
