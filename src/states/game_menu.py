
from __future__ import annotations
from typing import Any, Callable
from pathlib import Path

import pygame

from .menu import Menu
from states.instructions import Instructions


class GameMenu:
    """e
    Menu state: main, configuration, highest-score and instructions
    screens.

    Keyboard: Up/Down select (or scroll on the instructions screen),
    Enter presses the selected button, Backspace goes back to the main
    menu from any other screen.

    Parameters
    ------------------------------------------
    size : tuple of int
        Window size ``(width, height)``.
    font : pygame.font.Font
        Font for buttons and scores.
    title_font : pygame.font.Font
        Font for the screen title.
    functions : dict of str to callable
        Callbacks provided by the game. Required keys: ``"start"`` and
        ``"exit"``. Optional key: ``"set_option"``, called with the value
        chosen in the configuration menu.
    scores : list of str, optional
        Lines shown in the highest-score screen.

    Attributes
    ------------------------------------------
    menu : Menu
        Menu currently displayed.
    title : str
        Title of the current screen.
    current : str
        Name of the current screen (``"main"``, ``"config"``, ``"score"``).
    instructions : Instructions
        Scrollable instructions content.
    """

    # TODO make adaptative size in base the main size
    # ? I Have not idea how to do this ^ 😢
    BUTTON_SIZE = (220, 56)
    FOOTER_MARGIN = 24
    #ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
    TITLE_COLOR = (0, 220, 0)
    SCORE_COLOR = (120, 120, 120)

    def __init__(self, size: tuple[int, int], font: Any, title_font: Any,
                 functions: dict[str, Callable[..., None]],
                 scores: list[str] | None = None,
                 path: Path = Path(".")) -> None:
        self.WIDTH, self.HEIGHT = size
        self.functions = functions
        self.font = font
        self.title_font = title_font
        self.scores = scores if scores is not None else [
            "Player1    4610", "Player2    3170", "Player3    2840"]
        self.normal, self.active = self._make_images()
        self.normal, self.active = self._make_images()
        self.footer_y = self.HEIGHT - self.BUTTON_SIZE[1] - self.FOOTER_MARGIN
        self.assets_dir = path
        viewport = pygame.Rect(20, 100, self.WIDTH - 40,
                               self.footer_y - 12 - 100)
        self.instructions = Instructions(viewport, font, self.assets_dir)

        self.menus: dict[str, tuple[str, Callable[[], Menu]]] = {
            "main": ("Main menu", self._make_main_menu),
            "instructions": ("Instructions", self._make_instructions_menu),
            "config": ("Configuration", self._make_config_menu),
            "score": ("Highest Score", self._make_score_menu),
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

    # ---- menu factories ----------------------------------------------
    def _new_menu(self, items: list[str], actions: list[Callable[[], None]],
                  title_case: bool = True, y: int = 120) -> Menu:
        x = (self.WIDTH - self.BUTTON_SIZE[0]) // 2
        return Menu(items, actions, x=x, y=y,
                    image_normal=self.normal, image_active=self.active,
                    font=self.font, title_case=title_case)

    def _make_main_menu(self) -> Menu:
        """Build the main menu."""
        return self._new_menu(
            ["Start", "instructions", "Configuration", "Highest Score", "Exit"],
            [self.functions["start"],
             lambda: self.change_menu("instructions"),
             lambda: self.change_menu("config"),
             lambda: self.change_menu("score"),
             self.functions["exit"]],
        )

    # TODO Add options to configure from here like difficulto or whatever.
    def _make_config_menu(self) -> Menu:
        """Build the configuration menu."""
        return self._new_menu(
            ["3s", "5s", "10s", "Return"],
            [lambda: self.set_option(3),
             lambda: self.set_option(5),
             lambda: self.set_option(10),
             lambda: self.change_menu("main")],
            title_case=False,
        )

    def _make_score_menu(self) -> Menu:
        """Build the highest-score menu (scores are drawn in `draw`)."""
        return self._new_menu(
            ["Return"],
            [lambda: self.change_menu("main")],
            y=320,
            title_case=False,
        )

    def _make_instructions_menu(self) -> Menu:
        """Build the instructions menu (a Return button in the footer)."""
        return self._new_menu(
            ["Return"],
            [lambda: self.change_menu("main")],
            y=self.footer_y,
            title_case=False,
        )

    # ---- actions -----------------------------------------------------
    def set_option(self, value: int) -> None:
        """Report the chosen value to the game and go back to main."""
        callback = self.functions.get("set_option")
        if callback is not None:
            callback(value)
        self.change_menu("main")

    def change_menu(self, name: str) -> None:
        """Replace the displayed menu by the one registered as `name`."""
        self.current = name
        self.title, factory = self.menus[name]
        self.menu = factory()
        if name == "instructions":
            self.instructions.reset()

    # ---- PYGAME: events and drawing ---------------------------------
    def handle_event(self, event: Any) -> bool:
        """Forward a pygame event to the current menu.

        Returns
        -------
        bool
            True if the event was valid for the menu.
        """
        if (event.type == pygame.KEYDOWN
                and event.key == pygame.K_BACKSPACE
                and self.current != "main"):
            self.change_menu("main")
            return True
        if self.current == "instructions" \
                and self.instructions.handle_event(event):
            return True
        return self.menu.handle_event(event)

    # * I can not manage to do scroll without this here
    def update(self) -> None:
        """Per-frame update (continuous scrolling on instructions)."""
        if self.current == "instructions":
            self.instructions.update()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title, the current menu and, if needed, the scores."""
        title = self.title_font.render(self.title, True, self.TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(self.WIDTH // 2, 60)))
        if self.current == "instructions":
            self.instructions.draw(surface)
        self.menu.draw(surface)
        if self.current == "score":
            self._draw_scores(surface)

    def _draw_scores(self, surface: pygame.Surface) -> None:
        """Draw the score lines below the title."""
        y = 130
        for line in self.scores:
            text = self.font.render(line, True, self.SCORE_COLOR)
            surface.blit(text, text.get_rect(center=(self.WIDTH // 2, y)))
            y += 30
