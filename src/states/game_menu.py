
from __future__ import annotations
from typing import Any, Callable
from pathlib import Path

import pygame

from .menu import Menu
from src.states.instructions import Instructions


class GameMenu:
    """e
    Menu state: main, configuration, highest-score, instructions, pause and
    game-over screens.

    Keyboard: Up/Down select (or scroll on the instructions screen),
    Enter presses the selected button, Backspace returns to the previous
    menu or resumes the game from pause.

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
        ``"exit"``. Pause uses ``"resume"`` and optionally ``"get_scores"``.
        Configuration uses ``"get_settings"`` and ``"set_setting"``.
        Game-over screens also use ``"save_score"``, ``"return_to_main"``
        and ``"start"``.
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
    FOOTER_MARGIN = 124
    # ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
    TITLE_COLOR = (64, 80, 100)
    SCORE_COLOR = (120, 120, 120)
    BORDER_COLOR = (80, 180, 250)
    BORDER_COLOR_PRESS = (40, 140, 220)
    CONFIG_SIZE = (400, 56)
    CONFIG_OPTIONS = (
        ("graphics", ("SD", "HD")),
        ("screen", ("Window", "Full")),
        ("music", ()),
        ("speed", (0.8, 1.0, 1.2)),
        ("cheats", (False, True)),
    )
    #BOTTOM_PADDIN = 80

    def __init__(self, size: tuple[int, int], font: Any, title_font: Any,
                 functions: dict[str, Callable[..., Any]],
                 scores: list[str] | None = None,
                 path: Path = Path(".")) -> None:
        self.WIDTH, self.HEIGHT = size
        self.functions = functions
        self.font = font
        self.title_font = title_font
        self.scores = scores if scores is not None else []
        self.score_status = ""
        self.pause_score = 0
        self.instructions_return = "main"
        self.final_score = 0
        self.player_name = ""
        self.game_over_status = ""
        self._dragging_volume = False
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
            "pause": ("Pause menu", self._make_pause_menu),
            "cheats": ("Cheat menu", self._make_cheat_menu),
            "game_over": ("Game Over", self._make_game_over_menu),
        }
        self.change_menu("main")

    def _make_images(self, size: tuple[int, int] | None = None
                     ) -> tuple[pygame.Surface, pygame.Surface]:
        """Build the normal/active button surfaces without asset files."""
        def build(fill: tuple[int, int, int],
                  border: tuple[int, int, int]) -> pygame.Surface:
            image = pygame.Surface(size or self.BUTTON_SIZE, pygame.SRCALPHA)
            rect = image.get_rect()
            pygame.draw.rect(image, fill, rect, border_radius=10)
            pygame.draw.rect(image, border, rect, width=3, border_radius=10)
            return image

        return build((30, 30, 30), self.BORDER_COLOR), build((15, 15, 15),
                                                        self.BORDER_COLOR_PRESS)

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
            ["Start", "instructions", "Configuration", "Highest Score",
             "Exit"],
            [self.functions["start"],
             lambda: self.change_menu("instructions"),
             lambda: self.change_menu("config"),
             lambda: self.change_menu("score"),
             self.functions["exit"]],
        )

    def _make_config_menu(self) -> Menu:
        """Build the configuration menu."""
        normal, active = self._make_images(self.CONFIG_SIZE)
        actions = [lambda index=index: self._adjust_config(index, 1)
                   for index in range(len(self.CONFIG_OPTIONS))]
        actions.append(lambda: self.change_menu("main"))
        menu = Menu(self._config_labels() + ["Return"], actions,
                    x=(self.WIDTH - self.CONFIG_SIZE[0]) // 2, y=120,
                    image_normal=normal, image_active=active,
                    font=self.font, title_case=False)
        return menu

    def _config_labels(self) -> list[str]:
        settings = self.functions["get_settings"]()
        speed = {0.8: "Slow", 1.0: "Medium", 1.2: "Fast"}[settings["speed"]]
        return [f"Graphics: {settings['graphics']}",
                f"Screen: {settings['screen']}",
                f"Music Level: {settings['music']}%",
                f"Speed: {speed}",
                f"Cheat mode: {'On' if settings['cheats'] else 'Off'}"]

    def _adjust_config(self, index: int, step: int) -> None:
        name, choices = self.CONFIG_OPTIONS[index]
        current = self.functions["get_settings"]()[name]
        if name == "music":
            value = max(0, min(100, current + step * 5))
        else:
            value = choices[(choices.index(current) + step) % len(choices)]
        self.functions["set_setting"](name, value)
        for button, label in zip(self.menu.buttons, self._config_labels()):
            button.text = label

    def _volume_rect(self) -> pygame.Rect:
        rect = self.menu.buttons[2].rect
        return pygame.Rect(rect.x + 35, rect.bottom - 12, rect.width - 70, 5)

    def _set_volume_from_mouse(self, x: int) -> None:
        rect = self._volume_rect()
        value = round(max(0, min(rect.width, x - rect.left)) * 100 / rect.width)
        self.functions["set_setting"]("music", value)
        self.menu.buttons[2].text = self._config_labels()[2]

    def resize(self, size: tuple[int, int]) -> None:
        """Relayout the current menu after changing display mode."""
        selected = self.menu.selected
        self.WIDTH, self.HEIGHT = size
        self.footer_y = self.HEIGHT - self.BUTTON_SIZE[1] - self.FOOTER_MARGIN
        viewport = pygame.Rect(20, 100, self.WIDTH - 40,
                               self.footer_y - 12 - 100)
        self.instructions = Instructions(viewport, self.font, self.assets_dir)
        self.menu = self.menus[self.current][1]()
        self.menu.selected = min(selected, len(self.menu.buttons) - 1)
        self.menu._sync_focus()

    def _make_score_menu(self) -> Menu:
        """Build the highest-score menu (scores are drawn in `draw`)."""
        return self._new_menu(
            ["Return"],
            [lambda: self.change_menu("main")],
            y=self.footer_y,
            title_case=False,
        )

    def _make_instructions_menu(self) -> Menu:
        """Build the instructions menu (a Return button in the footer)."""
        return self._new_menu(
            ["Return"],
            [lambda: self.change_menu(self.instructions_return)],
            y=self.footer_y,
            title_case=False,
        )

    def _make_pause_menu(self) -> Menu:
        """Build the pause menu."""
        items = ["Return", "Instructions"]
        actions = [self.functions["resume"],
                   lambda: self.change_menu("instructions")]
        if self.functions["get_settings"]()["cheats"]:
            items.append("Cheat Menu")
            actions.append(lambda: self.change_menu("cheats"))
        items.append("Exit")
        actions.append(self.functions["exit"])
        return self._new_menu(items, actions, y=320, title_case=False)

    def _cheat_labels(self) -> list[str]:
        cheats = self.functions["get_cheats"]()
        return [f"[{'x' if cheats[name] else ' '}] {label}"
                for name, label in (("invincible", "Invincible"),
                                    ("immortality", "Immortality"),
                                    ("flash_mode", "Flash Mode"),
                                    ("no_dash_cooldown",
                                     "Disable dash cooldown"))]

    def _make_cheat_menu(self) -> Menu:
        normal, active = self._make_images(self.CONFIG_SIZE)
        return Menu(
            self._cheat_labels() + ["[ ] Next Level", "Spawn random fruit",
                                    "Return"],
            [lambda: self._toggle_cheat("invincible"),
             lambda: self._toggle_cheat("immortality"),
             lambda: self._toggle_cheat("flash_mode"),
             lambda: self._toggle_cheat("no_dash_cooldown"),
             self.functions["next_level"],
             self.functions["spawn_fruit"],
             lambda: self.change_menu("pause")],
            x=(self.WIDTH - self.CONFIG_SIZE[0]) // 2, y=120,
            image_normal=normal, image_active=active,
            font=self.font, title_case=False)

    def _toggle_cheat(self, name: str) -> None:
        self.functions["toggle_cheat"](name)
        for button, label in zip(self.menu.buttons, self._cheat_labels()):
            button.text = label

    def _make_game_over_menu(self) -> Menu:
        return self._new_menu(
            ["Save score", "Restart", "Return"],
            [self._save_score, self.functions["start"],
             self.functions["return_to_main"]],
            y=320,
            title_case=False,
        )

    def show_game_over(self, score: int) -> None:
        self.final_score = score
        self.player_name = ""
        self.game_over_status = ""
        self.change_menu("game_over")

    def show_victory(self, score: int) -> None:
        self.show_game_over(score)
        self.title = "Victory!"

    def show_pause(self, score: int) -> None:
        self.pause_score = score
        self.change_menu("pause")

    def _save_score(self) -> None:
        name = self.player_name.strip()
        if len(name) < 2:
            self.game_over_status = "Name must have at least 2 characters."
            return
        try:
            self.functions["save_score"](name, self.final_score)
        except (OSError, ValueError) as error:
            self.game_over_status = f"Could not save score: {error}"
            return
        self.game_over_status = "Score saved."

    # ---- actions -----------------------------------------------------
    def change_menu(self, name: str) -> None:
        """Replace the displayed menu by the one registered as `name`."""
        self._dragging_volume = False
        if name == "instructions":
            self.instructions_return = (
                "pause" if getattr(self, "current", None) == "pause"
                else "main")
        if getattr(self, "current", None) == "game_over":
            pygame.key.stop_text_input()
        self.current = name
        self.title, factory = self.menus[name]
        self.menu = factory()
        if name == "instructions":
            self.instructions.reset()
        elif name == "game_over":
            pygame.key.start_text_input()
        elif name in ("score", "pause") and "get_scores" in self.functions:
            try:
                self.scores = self.functions["get_scores"]()
                self.score_status = ""
            except (OSError, ValueError) as error:
                self.scores = []
                self.score_status = f"Could not load scores: {error}"

    # ---- PYGAME: events and drawing ---------------------------------
    def handle_event(self, event: Any) -> bool:
        """Forward a pygame event to the current menu.

        Returns
        -------
        bool
            True if the event was valid for the menu.
        """
        if self.current == "game_over":
            if event.type == pygame.TEXTINPUT:
                if event.text.isprintable():
                    self.player_name = (self.player_name + event.text)[:24]
                    self.game_over_status = ""
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                    self.game_over_status = ""
                    return True
                if event.key not in (pygame.K_UP, pygame.K_DOWN,
                                     pygame.K_RETURN, pygame.K_KP_ENTER):
                    return True
            if event.type == pygame.KEYUP and event.key == pygame.K_BACKSPACE:
                return True
        if (event.type == pygame.KEYDOWN
                and event.key == pygame.K_BACKSPACE
                and self.current != "main"):
            if self.current == "pause":
                self.functions["resume"]()
            elif self.current == "instructions":
                self.change_menu(self.instructions_return)
            elif self.current == "cheats":
                self.change_menu("pause")
            else:
                self.change_menu("main")
            return True
        if self.current == "instructions" \
                and self.instructions.handle_event(event):
            return True
        if self.current == "config":
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_LEFT, pygame.K_RIGHT):
                index = self.menu.selected
                if index < len(self.CONFIG_OPTIONS):
                    self._adjust_config(index, -1 if event.key == pygame.K_LEFT
                                        else 1)
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                    and self.menu.buttons[2].rect.collidepoint(event.pos):
                self.menu.hover(event.pos)
                self._dragging_volume = True
                self._set_volume_from_mouse(event.pos[0])
                return True
            if event.type == pygame.MOUSEMOTION and self._dragging_volume:
                self._set_volume_from_mouse(event.pos[0])
                return True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 \
                    and self._dragging_volume:
                self._dragging_volume = False
                self._set_volume_from_mouse(event.pos[0])
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
        if self.current == "config":
            rect = self._volume_rect()
            pygame.draw.rect(surface, (60, 60, 60), rect)
            fill = rect.copy()
            fill.width = round(rect.width * self.functions["get_settings"]()["music"] / 100)
            pygame.draw.rect(surface, self.TITLE_COLOR, fill)
        elif self.current == "score":
            self._draw_scores(surface)
        elif self.current == "pause":
            self._draw_pause(surface)
        elif self.current == "game_over":
            self._draw_game_over(surface)

    def _draw_scores(self, surface: pygame.Surface) -> None:
        """Draw the score lines below the title."""
        y = 130
        for line in self.scores:
            text = self.font.render(line, True, self.SCORE_COLOR)
            surface.blit(text, text.get_rect(center=(self.WIDTH // 2, y)))
            y += 30
        if self.score_status:
            text = self.font.render(self.score_status, True, self.SCORE_COLOR)
            surface.blit(text, text.get_rect(center=(self.WIDTH // 2, y)))

    def _draw_game_over(self, surface: pygame.Surface) -> None:
        for y, line in ((140, f"Score: {self.final_score}"),
                        (205, f"Name: {self.player_name}_"),
                        (260, self.game_over_status)):
            text = self.font.render(line, True, self.SCORE_COLOR)
            surface.blit(text, text.get_rect(center=(self.WIDTH // 2, y)))

    def _draw_pause(self, surface: pygame.Surface) -> None:
        score = self.title_font.render(f"Score: {self.pause_score}", True,
                                       self.TITLE_COLOR)
        surface.blit(score, score.get_rect(center=(self.WIDTH // 2, 120)))
        lines = ["Top 3 players", *self.scores[:3]]
        if self.score_status:
            lines.append(self.score_status)
        for index, line in enumerate(lines):
            text = self.font.render(line, True, self.SCORE_COLOR)
            surface.blit(text, text.get_rect(
                center=(self.WIDTH // 2, 170 + index * 30)))
