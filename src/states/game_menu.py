from __future__ import annotations

from typing import Any, Callable, Iterator
import pygame
from menu import Menu


class GameMenu:

    ## TODO make adaptative size in base the main size
    #WIDTH, HEIGHT = 480, 660
    BUTTON_SIZE = (220, 56)

    def __init__(self, size, functions: list[Callable]):
        self.WIDTH, self.HEIGHT = size
        self.functions = functions
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.normal, self.active = self._make_images()
        self.menus: dict[str, tuple[str, Callable[[], Menu]]] = {
            "main": ("Main menu", self._make_main_menu),
            "config": ("Configuration", self._make_config_menu),
            "score": ("Highest Score", self._make_score_menu)
        }
        self.change_menu("main")

    def _make_images(self) -> tuple[pygame.Surface, pygame.Surface]:
        """Build the normal/active button surfaces without asset files."""
        def build(fill: tuple[int, int, int],
                  border: tuple[int, int, int]) -> pygame.Surface:
            image = pygame.Surface(self.BUTTON_SIZE, pygame.SRCALPHA)
            rect = image.get_rect()
            pygame.draw.rect(image, fill, rect, border_radius=10)
            pygame.draw.rect(image, border, rect, width=3, border_radius=10)
            return image

        return build((30, 30, 30), (0, 150, 0)), build((15, 15, 15),
                                                        (0, 255, 0))

    def _new_menu(self, items: list[str], actions: list[Callable[[], None]],
                  title_case: bool = True, y=120) -> Menu:
        x = (self.WIDTH - self.BUTTON_SIZE[0]) // 2
        return Menu(items, actions, x=x, y=y,
                    image_normal=self.normal, image_active=self.active,
                    font=self.font, title_case=title_case)

    def _make_main_menu(self) -> Menu:
        return self._new_menu(
            ["Start", "Configuration", "Highest Score", "Exit"],
            [self.functions["start"],
             lambda: self.change_menu("config"),
             lambda: self.change_menu("score"),
             self.functions["exit"]],
        )

    def _make_config_menu(self) -> Menu:
        """ Build Config menu """
        return self._new_menu(
            ["3s", "5s", "10s", "Return"],
            [lambda: self.default_name(3),
             lambda: self.default_name(5),
             lambda: self.default_name(10),
             lambda: self.change_menu("main")],
            title_case=False,
        )

    def default_name(self, value: int) -> None:
        pass

    def _make_score_menu(self) -> Menu:
        """ Show top scores """
        return self._new_menu(
            ["Return"],
            [lambda: self.change_menu("main")],
            y=320,
            title_case=False,
        )

    def change_menu(self, name: str) -> None:
        """Replace the displayed menu by the one registered as `name`."""
        self.title, factory = self.menus[name]
        self.menu = factory()
