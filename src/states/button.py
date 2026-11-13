from typing import Any, Callable
import pygame


class Button:
    """
    Animated, interactive button drawn with images.

    The button swaps between a normal and an active image, shifts its
    position when active, and changes text color on mouse hover.

    Parameters
    ------------------------------------------
    x : int
        X coordinate of the button's top-left corner.
    y : int
        Y coordinate of the button's top-left corner.
    image_normal : pygame.Surface
        Surface used when the button is not active.
    image_active : pygame.Surface
        Surface used when the button is active.
    text : str, optional
        String displayed on the button. Default is ``""``.
    font : pygame.font.Font, optional
        Font used to render the text. If None, a default font of size 32
        is created.
    text_color : tuple of int, optional
        Normal text color as an RGB tuple. Default is ``(0, 200, 0)``.
    text_hover : tuple of int, optional
        Text color as an RGB tuple while the mouse hovers over the
        button. Default is ``(0, 255, 0)``.
    active_offset : tuple of int, optional
        ``(dx, dy)`` distance the button moves when active. Default is
        ``(0, 2)``.

    Attributes
    ------------------------------------------
    image_normal : pygame.Surface
        Surface used when the button is not active.
    image_active : pygame.Surface
        Surface used when the button is active.
    image : pygame.Surface
        Surface currently displayed.
    action : callable
        Callback invoked when the button is triggered.
    base_pos : tuple of int
        Original top-left position of the button.
    active_offset : tuple of int
        ``(dx, dy)`` shift applied while the button is active.
    rect : pygame.Rect
        Rectangle used for positioning and collision detection.
    text : str
        String displayed on the button.
    font : pygame.font.Font
        Font used to render the text.
    text_color : tuple of int
        Normal text color as an RGB tuple.
    hover_color : tuple of int
        Text color while the mouse hovers over the button.
    is_hovered : bool
        True if the mouse is currently over the button.
    is_active : bool
        True if the button is currently active.
    """
    def __init__(self,
                 x: int,
                 y: int,
                 image_normal: Any,
                 image_active: Any,
                 text: str = "",
                 font: Any = None,
                 text_color: tuple[int, int, int] = (0, 200, 0),
                 text_hover: tuple[int, int, int] = (0, 255, 0),
                 active_offset: tuple[int, int] = (0, 2)
                 ) -> None:
        self.image_normal = image_normal
        self.image_active = image_active
        self.image = self.image_normal
        self.action: Callable[[], None] | Callable[[Any], None] = lambda: None
        # Positions
        self.base_pos = (x, y)
        self.active_offset = active_offset
        self.rect = self.image.get_rect(topleft=self.base_pos)

        # Text
        self.text = text
        self.font = font or pygame.font.Font(None, 32)
        self.text_color = text_color
        self.hover_color = text_hover

        # State
        self.is_hovered = False
        self.is_active = False

    def handle_event(self, event: Any) -> bool:
        """ Manage interactions and states with the button """

        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_active = True
                self._update_visual_state()
                return False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_active = False
                self._update_visual_state()
                return True

        return False

    def _update_visual_state(self) -> None:
        """ Switch image and position based on button state """
        if self.is_active:
            self.image = self.image_active
            new_x = self.base_pos[0] + self.active_offset[0]
            new_y = self.base_pos[1] + self.active_offset[1]
            self.rect = self.image.get_rect(topleft=(new_x, new_y))

        else:
            self.image = self.image_normal
            self.rect = self.image.get_rect(topleft=self.base_pos)

    def hover(self, mouse_pos: Any) -> None:
        """ Manage hover effect on text """
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: Any) -> None:
        """ Create the button in the screen """
        surface.blit(self.image, self.rect)

        color = self.hover_color if self.is_hovered else self.text_color
        text_button = self.font.render(self.text, True, color)
        text_rect = text_button.get_rect(center=self.rect.center)
        surface.blit(text_button, text_rect)
