import pygame
from __future__ import annotations
from typing import Any, Callable
from states.game_menu import GameMenu

# TODO Read screen size

TICK = pygame.USEREVENT + 1
ENTER_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)

class Game:
    SCREEN_SIZE = (480, 660)

    def __init__(self, config):
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.config = config

    def _pre_init(self) -> None:
        """ Load Starting resoruces """
        functions = {
            "start": self.start,
            "finish": self.exit_app,
        }
        self.running = True
        pygame.display.set_caption('Pacman')
        self._menu = GameMenu(self.SCREEN_SIZE, functions)

    def run(self) -> None:
        """ Run the application """
        self._pre_init()
        self._init()
        self._play_theme()
        self._config()
        self._update()
        self._finish()

    def _init(self) -> None:
        """ Load graphics """
        pass

    def start(self) -> None:
        """ Start the game """
        print("Running the game")

    def _play_theme(self) -> None:
        """ A """
        pass

    def _config(self) -> None:
        """ A """
        pass

    def _update(self) -> None:
        """ Main loop """
        while self.running:
            self.event_loop()
            self.draw()
            self.clock.tick(60)

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

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == TICK:
                self.ticks += 1
                print(f"Counter: {self.ticks * self.interval}s elapsed")
            else:
                self.menu.handle_event(event)

    def _finish(self) -> None:
        """ Finish something """
        pass

    def exit_app(self) -> None:
        """ Exit from the application """
        self.running = False
