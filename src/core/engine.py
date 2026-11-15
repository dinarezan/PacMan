
from __future__ import annotations

import pygame
from states.game_menu import GameMenu

# TODO Read screen size


class Engine:
    """
    Main application: owns the window, the main loop and the game states.

    Parameters
    ------------------------------------------
    config : Any
        Application configuration.

    Attributes
    ------------------------------------------
    SCREEN_SIZE : tuple of int
        Window size ``(width, height)``.
    running : bool
        True while the main loop is active.
    option : int or None
        Value chosen in the configuration menu, if any.
    """

    SCREEN_SIZE = (480, 660)
    BACKGROUND = (10, 10, 10)

    def __init__(self, config):
        pygame.init()
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.config = config
        self.running = False
        self.option: int | None = None

    # -- Init stuff ----------------------------------------------------
    def _pre_init(self) -> None:
        """Load starting resources."""
        pygame.display.set_caption('Pacman')
        functions = {
            "start": self.start,
            "exit": self.exit_app,
            "set_option": self.set_option,
        }
        self.running = True
        self._menu = GameMenu(
            size=self.SCREEN_SIZE,
            font=self.font,
            title_font=self.title_font,
            functions=functions,
        )

    def run(self) -> None:
        """Run the application."""
        self._pre_init()
        self._init()
        self._play_theme()
        self._config()
        self._update()
        self._finish()

    def _init(self) -> None:
        """Load graphics."""
        pass

    def start(self) -> None:
        """Start the game."""
        print("Running the game")

    def set_option(self, value: int) -> None:
        """Store the value chosen in the configuration menu."""
        self.option = value
        print(f"Option set to {value}")

    def _play_theme(self) -> None:
        """Play the theme music."""
        pass

    def _config(self) -> None:
        """Apply the configuration."""
        pass

    # ! -- MAIN LOOP --------------------------------------------------
    def _update(self) -> None:
        """Main loop."""
        while self.running:
            self.event_loop()
            self.draw()
            self.clock.tick(60)

    def update(self) -> None:
        """Per-frame logic."""
        self._menu.update()

    def draw(self) -> None:
        """Clear the screen, draw the active state and present the frame.

        The Game owns the window, so it clears and flips; each state
        (here ``GameMenu``) is responsible for drawing its own content.
        """
        self.screen.fill(self.BACKGROUND)
        self._menu.draw(self.screen)
        pygame.display.flip()

    def event_loop(self) -> None:
        """Dispatch pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self._menu.handle_event(event)

    def _finish(self) -> None:
        """Release resources."""
        pygame.quit()

    def exit_app(self) -> None:
        """Exit from the application."""
        self.running = False
