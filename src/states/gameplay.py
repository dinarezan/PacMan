import pygame

from typing import Any
from src.map.render_map import RenderMap


class Gameplay:

    def __init__(self, renderer: RenderMap):
        self.renderer = renderer

# ---- PYGAME: events and drawing ---------------------------------
    def handle_event(self, event: Any) -> bool:
        """Forward a pygame event to the current menu.

        Returns
        -------
        bool
            True if the event was valid for the menu.
        """

        # ? Addd a lapse before start the game and then ctrl it.
        if (event.type == pygame.KEYDOWN and self.renderer.game_init):
            print("Key is working")
            #pacman = getattr(self.renderer.map, "pacman", ())
            pacman = self.renderer.map.pacman
            #if pacman.speed ==
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    pacman.direction = 0
                    return True
                elif event.key == pygame.K_d:
                    pacman.direction = 1
                    return True
                elif event.key == pygame.K_s:
                    pacman.direction = 2
                    return True
                elif event.key == pygame.K_a:
                    pacman.direction = 3
                    return True
        return False




        #if (event.type == pygame.KEYDOWN
        #        and event.key == pygame.K_BACKSPACE
        #        and self.current != "main"):
        #    self.change_menu("main")
        #    return True
        #if self.current == "instructions" \
        #        and self.instructions.handle_event(event):
        #    return True
        #return self.menu.handle_event(event)