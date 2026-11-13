"""Keyboard- and mouse-driven menu demo built with pygame.

Controls
--------
Up / Down : move the selection to the previous / next button.
Enter     : press the selected button.
Mouse     : hover to select, click to press.
"""

from __future__ import annotations

from typing import Any, Callable, Iterator

import pygame
from menu import Menu

TICK = pygame.USEREVENT + 1
ENTER_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)


# ----------------------------------------------------------------------
# Example application
# ----------------------------------------------------------------------
class App:
    """
    Demo with a main menu and a configuration menu.

    Attributes
    ----------
    interval : int
        Seconds between counter prints.
    ticks : int
        Number of prints since the counter was started.
    counting : bool
        True while the counter is running.
    menu : Menu
        The menu currently displayed.
    """

    WIDTH, HEIGHT = 480, 660
    BUTTON_SIZE = (220, 56)

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Menu demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.normal, self.active = self._make_images()

        self.interval = 5
        self.ticks = 0
        self.counting = False
        self.running = True

        self.menus: dict[str, tuple[str, Callable[[], Menu]]] = {
            "main": ("Main menu", self._make_main_menu),
            "config": ("Configuration", self._make_config_menu),
            "score": ("Highest Score", self._make_score_menu)
        }
        self.title = ""
        self.menu = self._make_main_menu()
        self.change_menu("main")

    # -- assets --------------------------------------------------------
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

    # -- menu factories ------------------------------------------------
    def _new_menu(self, items: list[str], actions: list[Callable[[], None]],
                  title_case: bool = True, y=120) -> Menu:
        x = (self.WIDTH - self.BUTTON_SIZE[0]) // 2
        return Menu(items, actions, x=x, y=y,
                    image_normal=self.normal, image_active=self.active,
                    font=self.font, title_case=title_case)

    def _make_main_menu(self) -> Menu:
        return self._new_menu(
            ["Start", "Configuration", "Highest Score", "Exit"],
            [self.start_counter,
             lambda: self.change_menu("config"),
             lambda: self.change_menu("score"),
             self.exit_app],
        )

    def _make_config_menu(self) -> Menu:
        # title_case=False so "3s" is not turned into "3S"
        return self._new_menu(
            ["3s", "5s", "10s", "Return"],
            [lambda: self.set_interval(3),
             lambda: self.set_interval(5),
             lambda: self.set_interval(10),
             lambda: self.change_menu("main")],
            title_case=False,
        )

    def _make_score_menu(self) -> Menu:
        # title_case=False so "3s" is not turned into "3S"
        return self._new_menu(
            ["Return"],
            [lambda: self.change_menu("main")],
            y=320,
            title_case=False,
        )

    # -- actions -------------------------------------------------------
    def change_menu(self, name: str) -> None:
        """Replace the displayed menu by the one registered as `name`."""
        self.title, factory = self.menus[name]
        self.menu = factory()

    def start_counter(self) -> None:
        """Start (or restart) the counter."""
        self.ticks = 0
        self.counting = True
        pygame.time.set_timer(TICK, self.interval * 1000)
        print(f"Counter started: printing every {self.interval}s")

    def set_interval(self, seconds: int) -> None:
        """Set the print interval and go back to the main menu."""
        self.interval = seconds
        if self.counting:
            self.start_counter()
        self.change_menu("main")

    def exit_app(self) -> None:
        """Stop the main loop."""
        self.running = False

    # -- main loop -----------------------------------------------------
    def draw(self) -> None:
        """Render title, menu and status line."""
        self.screen.fill((10, 10, 10))
        title = self.title_font.render(self.title, True, (0, 220, 0))
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, 60)))
        self.menu.draw(self.screen)

        if self.menu.buttons[0].text == "Return":
            list = ["Player1    4610", "Player2    3170", "Player3    2840"]
            position = 130
            for item in list:
                scores = self.font.render(
                    item,
                    True, (120, 120, 120))
                self.screen.blit(scores,
                                 scores.get_rect(center=(self.WIDTH // 2, position)))
                position += 30

        state = (f"running, {self.ticks} prints" if self.counting
                 else "stopped")
        status = self.font.render(
            f"Interval: {self.interval}s | Counter: {state}",
            True, (120, 120, 120))
        self.screen.blit(status,
                         status.get_rect(center=(self.WIDTH // 2, 430)))
        pygame.display.flip()

    def run(self) -> None:
        """Run the event/draw loop until the user exits."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == TICK:
                    self.ticks += 1
                    print(f"Counter: {self.ticks * self.interval}s elapsed")
                else:
                    self.menu.handle_event(event)
            self.draw()
            self.clock.tick(60)
        pygame.time.set_timer(TICK, 0)
        pygame.quit()


if __name__ == "__main__":
    App().run()
