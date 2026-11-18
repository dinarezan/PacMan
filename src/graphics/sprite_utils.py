import pygame
import colorsys
from typing_extensions import TypeAliasType, Any


Surface = TypeAliasType("Surface", pygame.surface.Surface)
# [key: Surface]
_processed_cache: dict[
    tuple[int, str | tuple[int, int, int], int],
    Surface] = {}

_palette_cache: dict[Any, Surface] = {}

_tone_cache: dict[Any, Surface] = {}


def tint_surface(surface: pygame.Surface, hue: float = 0.0,
                 saturation: float = 1.0,
                 luminosity: float = 1.0) -> pygame.Surface:
    """
    Return a copy of `surface` with `change_color` applied to every pixel.

    Transparency is preserved. Pixels are processed in Python (with a
    per-color cache), so call this once and keep the result; do not call
    it every frame.

    Parameters
    ----------
    surface : pygame.Surface
        32-bit surface to tint. It is not modified.
    hue, saturation, luminosity : float, optional
        See `change_color`.

    Returns
    -------
    pygame.Surface
        The tinted copy.
    """
    result = surface.copy()
    cache: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    width, height = result.get_size()
    for x in range(width):
        for y in range(height):
            r, g, b, a = result.get_at((x, y))
            if a == 0:
                continue
            new = cache.get((r, g, b))
            if new is None:
                new = cache[(r, g, b)] = change_color(
                    (r, g, b), hue, saturation, luminosity)
            result.set_at((x, y), (*new, a))
    return result


def get_tinted_image(base_image: Surface, color: tuple[int, int, int],
                     zoom: int, cache_key: str | None = None) -> Surface:
    """
    Generate new images with different colors and trasnarency.
    Adapt this images to current zoom.
    Cache it to improve speed.


    Parameters
    --------------------------------------------
    base_image      : Image (Pygame.Surface) to manipulate
    color           : Color to apply in RGB format: (255, 255, 255)
    zoom            : Zoom level apply to the image (size)
    cache_key       : Key name to cache it.
    --------------------------------------------
    return          : Tinted image.
    """
    zoom_key = round(zoom, 2)
    key = (id(base_image), cache_key or color, zoom_key)

    # If not cached, create it
    if key not in _processed_cache:
        image = base_image.copy()
        image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

        # Apply new zoom if is necceasy
        if zoom_key != 1.0:
            image = resize(image, zoom_key)

        _processed_cache[key] = image

    return _processed_cache[key]


def change_color(color: tuple[int, int, int],
                 hue: float = 0.0,
                 saturation: float = 1.0,
                 luminosity: float = 1.0
                 ) -> tuple[int, int, int]:
    """
    Convert a RGB image into HSV to manipulate these channels

    Parameters
    --------------------------------------------
    color : tuple of int
        Color in RGB, e.g. ``(255, 255, 255)``.

    hue : float, optional
        Degrees to rotate the hue. ``0`` keeps the color, ``180`` gives
        the opposite color, ``-30`` rotates backward.

    saturation : float, optional
        ``0.0`` is grayscale, ``1.0`` keeps the color, above ``1.0`` is
        more saturated.

    luminosity : float, optional
        Below ``1.0`` is darker, above ``1.0`` is lighter.

    Returns
    -------
    tuple of int
        The new color in RGB.
    """
    # Separate RGB Channels
    r, g, b = [c / 255 for c in color]
    # Convert RGB to HSV channels
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # Manipulate each channel
    h = (h + hue / 360.0) % 1.0
    s = max(0.0, min(1.0, s * saturation))
    v = max(0.0, min(1.0, v * luminosity))
    # Reconvert to RGB channels
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def generate_color_drone(base_image: Surface, hue_value: int,
                         zoom: int | float) -> Surface:
    """
    Remplace only a color base sprite for new color.
    (170, 81, 83)  -> color
    (100, 48, 49)  -> darker version of color

    Parameters
    --------------------------------------------
    base_image      : Image (Pygame.Surface) to manipulate
    color           : Color to apply in RGB format: (255, 255, 255)
    zoom            : Zoom level apply to the image (size)
    cache_key       : Key name to cache it.
    """
    zoom_key = round(zoom, 2)
    key = (id(base_image), hue_value, zoom_key)

    # Check buffer
    if key not in _tone_cache:
        image = base_image.copy()

        # Select new colors # ! Specific for this sprite
        color_map = {
            (170, 81, 83): change_color(color=(170, 81, 83), hue=hue_value),
            (100, 48, 49): change_color(color=(170, 81, 83), luminosity=0.6),
        }

        # Apply new colors in image
        for y in range(image.get_height()):
            for x in range(image.get_width()):
                r, g, b, a = image.get_at((x, y))

                new_color = color_map.get((r, g, b))
                if new_color:
                    image.set_at((x, y), (*new_color, a))

        if zoom_key != 1.0:
            image = resize(image, zoom_key)

        _tone_cache[key] = image

    return _tone_cache[key]


def resize(image: Surface, zoom_key: int | float) -> Surface:
    """ Transform the size of an image by zoom factor

    Parameters
    --------------------------------------------
    image       : image to resize
    zoom_key    : factor or value to resize the image
    """
    w, h = image.get_size()
    new_size = (max(1, int(w * zoom_key)), max(1, int(h * zoom_key)))
    image = pygame.transform.scale(image, new_size)

    return image
