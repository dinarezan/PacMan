from __future__ import annotations

from pathlib import Path
import pygame

from src.entities import Map
from src.entities.file_loaders import load_highscores, save_highscore
from src.states.game_menu import GameMenu
from src.graphics.asset_manager import AssetManager
from src.graphics.hud import Hud
from src.graphics.read_screen import read_screen_size
from src.map.render_map import RenderMap
from src.states.gameplay import Gameplay
# from src.core.settings import values   # * -> Put here game speed and other stuff??


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
    pause : bool
        True while the menu is shown instead of the game.
    speed : float
        Game-time multiplier applied to the frame time (1.0 is normal).
    option : int or None
        Value chosen in the configuration menu, if any.
    """


    BACKGROUND = (10, 10, 10)
    RESPAWN_DELAY = 1.0

    # def __init__(self, config,
    #                  highscore_path: str = str(Path("data") / "highscores.json")):
    def __init__(self, config,
                 highscore_path: str = ""):
        pygame.init()
        self.font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 48)
        self.screen = pygame.display.set_mode(read_screen_size())
        self.SCREEN_SIZE = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.speed = 1.0
        self.config = config
        self.highscore_path = highscore_path
        self.score = 0
        self.running = False
        self.pause = True
        self.game_active = False
        self.option: int | None = None
        self.renderer: RenderMap | None = None
        self.respawn_remaining = 0.0

    # -- Init stuff ----------------------------------------------------
    def _pre_init(self) -> None:
        """Load starting resources."""
        pygame.display.set_caption('Pacman')
        ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
        self.assets = AssetManager(ASSETS_DIR)
        functions = {
            "start": self.start,
            "exit": self.exit_app,
            "set_option": self.set_option,
            "save_score": self.save_score,
            "get_scores": self.get_scores,
            "return_to_main": self.return_to_main,
            "resume": self.resume,
        }
        self.running = True
        self._menu = GameMenu(
            size=self.SCREEN_SIZE,
            font=self.font,
            title_font=self.title_font,
            functions=functions,
            path=ASSETS_DIR,
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
        """Load graphics, and assets."""
        # self.assets.load_group("maps")

    def start(self) -> None:
        """Start the game."""
        if not self.config.levels:
            print("No more levels")
            return
        print("Running the game")
        self.renderer = self._create_renderer(0)
        self.gameplay = Gameplay(
            renderer=self.renderer,
            level=1,
            points=0,
            max_time=self.config.levels[0].max_time,
            lives=self.config.lives,
            points_per_pacgum=self.config.points_per_pacgum,
            points_per_super_pacgum=self.config.points_per_super_pacgum,
            ghosts_points=self.config.points_per_super_pacgum,
            )
        self.pause = False
        self.game_active = True
        self.score = 0
        self.respawn_remaining = 0.0
        self._menu.change_menu("pause")

    def _create_renderer(self, level_index: int) -> RenderMap:
        level = self.config.levels[level_index]
        game_map = Map(
            size=(level.width, level.height),
            seed=level.seed,
            ghosts=level.ghosts,
            pacgum=level.pacgum,
            max_time=level.max_time,
            points_per_pacgum=self.config.points_per_pacgum,
            points_per_super_pacgum=self.config.points_per_super_pacgum,
            points_per_ghost=self.config.points_per_ghost)
        # print("level:\n", game_map.maze)
        width, height = self.SCREEN_SIZE
        map_area = (width, height - Hud.TOP_HEIGHT - Hud.BOTTOM_HEIGHT)
        renderer = RenderMap(game_map, self.assets, map_area,
                             origin=(0, Hud.TOP_HEIGHT),
                             screen_size=self.SCREEN_SIZE)
        renderer.load_map()
        renderer.start_reveal(1.5)
        return renderer

    def _advance_level(self) -> None:
        next_index = self.gameplay.current_level
        if next_index >= len(self.config.levels):
            self.score = self.gameplay.points
            self.pause = True
            self.game_active = False
            self._menu.show_victory(self.score)
            return
        renderer = self._create_renderer(next_index)
        self.gameplay.advance_level(
            renderer, self.config.levels[next_index].max_time)
        self.renderer = renderer

    def set_option(self, value: int) -> None:
        """Store the value chosen in the configuration menu."""
        self.option = value
        print(f"Option set to {value}")
        # Difficult? Speed? Volumen? Cheat mode?

    def _play_theme(self) -> None:
        """Play the theme music."""
        pass

    def _config(self) -> None:
        """Apply the configuration."""
        pass

    def save_score(self, name: str, score: int) -> None:
        save_highscore(self.highscore_path, name, score)

    def get_scores(self) -> list[str]:
        scores = load_highscores(self.highscore_path).players
        return [f"{player.name}    {player.score}"
                for player in sorted(scores, key=lambda p: p.score,
                                     reverse=True)[:10]]

    def return_to_main(self) -> None:
        self.pause = True
        self.game_active = False
        self.renderer = None
        self.respawn_remaining = 0.0
        self._menu.change_menu("main")

    def resume(self) -> None:
        """Resume the active game without restarting it."""
        if self.game_active:
            self.pause = False

    # ----  MAIN LOOP ----------------------------------------------------
    def _update(self) -> None:
        """Main loop: events, logic, drawing (in this order)."""
        while self.running:
            # tick() caps the frame rate and returns the milliseconds
            # since the previous frame.
            dt = self.clock.tick(60) / 1000.0 * self.speed
            self.event_loop()
            self.update(dt)
            self.draw(dt)

    def update(self, dt: float) -> None:
        """Per-frame logic.

        Parameters
        ----------
        dt : float
            Seconds since the previous frame.
        """
        if self.pause:
            self._menu.update()
        elif self.respawn_remaining > 0:
            self.respawn_remaining = max(0.0, self.respawn_remaining - dt)
        elif self.renderer:
            self.renderer.update(dt)
            if self.gameplay:
                if (self.renderer.game_init and not self.renderer.revealing
                        and self.gameplay.level_complete):
                    self._advance_level()
                    return
                self.gameplay.update(dt)
                if self.gameplay.life_lost:
                    if self.gameplay.game_over:
                        self.score = self.gameplay.points
                        self.pause = True
                        self.game_active = False
                        self._menu.show_game_over(self.score)
                    else:
                        self.gameplay.reset_positions()
                        self.respawn_remaining = self.RESPAWN_DELAY
                elif (self.renderer.game_init and not self.renderer.revealing
                      and self.gameplay.level_complete):
                    self._advance_level()

    def draw(self, dt: float) -> None:
        """Clear the screen, draw the active state and present the frame.

        Everything must be drawn *before* ``flip()``: the screen is
        cleared at the start of every frame, so anything drawn after the
        flip is never shown.
        """
        self.screen.fill((0, 0, 0) if self.respawn_remaining > 0
                         and not self.pause else self.BACKGROUND)
        if self.pause:
            self._menu.draw(self.screen)
        elif self.respawn_remaining <= 0 and self.renderer:
            self.renderer.draw(self.screen, dt)
            if self.gameplay:
                self.gameplay.draw(self.screen)
        pygame.display.flip()

    def event_loop(self) -> None:
        """Dispatch pygame events to the active state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.respawn_remaining > 0 and not self.pause:
                continue
            elif self.pause:
                if (event.type == pygame.KEYDOWN
                        and event.key in (pygame.K_ESCAPE, pygame.K_p,
                                          pygame.K_SPACE)
                        and self._menu.current == "pause"):
                    self.resume()
                else:
                    self._menu.handle_event(event)
            elif (event.type == pygame.KEYDOWN
                  and event.key in (pygame.K_ESCAPE, pygame.K_p,
                                    pygame.K_SPACE)):
                self.pause = True
                self._menu.show_pause(self.gameplay.points)
            else:
                self.gameplay.handle_event(event)

    def _finish(self) -> None:
        """Release resources."""
        pygame.quit()

    def exit_app(self) -> None:
        """Exit from the application."""
        self.running = False
