import pygame


def read_screen_size() -> tuple[int, int]:
    """Return the primary display's desktop resolution in pixels.

    Pygame's display module must be initialized before calling this function.
    """
    sizes = pygame.display.get_desktop_sizes()
    if not sizes or sizes[0][0] <= 0 or sizes[0][1] <= 0:
        raise RuntimeError("Could not determine the primary display size")
    return sizes[0]
