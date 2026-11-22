from typing import Any, Callable, Iterator
import pygame

from .button import Button  # adjust to where your Button class lives


ENTER_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE)
#  K_KP_ENTER


class Menu:
    """
    Vertical menu of Buttons, usable with keyboard and mouse.

    Creates one `Button` per item and stacks them vertically, starting
    from the given top-left position. One button is always *selected*
    (highlighted); the selection moves with the Up/Down keys or when the
    mouse moves over a button.

    Parameters
    ------------------------------------------
    items : list of str
        Texts shown on each button.
    actions : list of callable
        One callable per text, in the same order as `items`.
    x : int
        X coordinate of the top-left corner of the first button.
    y : int
        Y coordinate of the top-left corner of the first button.
    image_normal : pygame.Surface
        Surface used when a button is not active.
    image_active : pygame.Surface
        Surface used when a button is active.
    font : pygame.font.Font, optional
        Font used to render the button texts. If None, `Button` creates
        a default font.
    spacing : int, optional
        Vertical distance between buttons. Default is ``70``.
    text_color : tuple of int, optional
        Normal text color as an RGB tuple. Default is ``(0, 200, 0)``.
    text_hover : tuple of int, optional
        Text color as an RGB tuple for the selected button. Default is
        ``(0, 255, 0)``.
    active_offset : tuple of int, optional
        ``(dx, dy)`` distance a button moves when pressed. Default is
        ``(0, 1)``.
    title_case : bool, optional
        If True, apply ``str.title()`` to every text. Default is ``True``.

    Attributes
    ------------------------------------------
    x : int
        X coordinate of the first button.
    y : int
        Y coordinate of the first button.
    image_normal : pygame.Surface
        Surface used when a button is not active.
    image_active : pygame.Surface
        Surface used when a button is active.
    font : pygame.font.Font or None
        Font passed to each button.
    spacing : int
        Vertical distance between buttons.
    text_color : tuple of int
        Normal text color as an RGB tuple.
    text_hover : tuple of int
        Text color of the selected button.
    active_offset : tuple of int
        ``(dx, dy)`` shift applied to a button when pressed.
    title_case : bool
        Whether button texts are converted with ``str.title()``.
    buttons : list of Button
        The buttons in the menu, in display order.
    selected : int
        Index of the currently selected button.

    Raises
    ------------------------------------------
    ValueError
        If `items` and `actions` do not have the same length.

    Examples
    ------------------------------------------
    >>> menu = Menu(["Start", "Exit"], [start, exit_app], x=130, y=120,
    ...             image_normal=normal, image_active=active)
    >>> for event in pygame.event.get():
    ...     menu.handle_event(event)
    >>> menu.draw(screen)
    """

    def __init__(
        self,
        items: list[str],
        actions: list[Callable[[], None]],
        x: int,
        y: int,
        image_normal: Any,
        image_active: Any,
        font: Any = None,
        spacing: int = 70,
        text_color: tuple[int, int, int] = (80, 180, 250),
        text_hover: tuple[int, int, int] = (170, 220, 255),
        active_offset: tuple[int, int] = (0, 1),
        title_case: bool = True,
    ) -> None:
        if len(items) != len(actions):
            raise ValueError(
                f"items ({len(items)}) and actions ({len(actions)}) "
                "must have the same length"
            )

        self.x = x
        self.y = y
        self.image_normal = image_normal
        self.image_active = image_active
        self.font = font
        self.spacing = spacing
        self.text_color = text_color
        self.text_hover = text_hover
        self.active_offset = active_offset
        self.title_case = title_case
        self.buttons: list[Button] = []
        self.selected = 0

        for text, action in zip(items, actions):
            self.add_button(text, action)

    # ---- Im lazy ---------------------------------------------------------
    def add_button(self, text: str, action: Callable[[], None]) -> Button:
        """
        Append a button below the last one and link its action.

        Parameters
        ----------
        text : str
            Text shown on the button.
        action : callable
            Callback run when the button is triggered.

        Returns
        -------
        Button
            The newly created button.
        """
        button = Button(
            x=self.x,
            y=self.y + len(self.buttons) * self.spacing,
            image_normal=self.image_normal,
            image_active=self.image_active,
            text=text.title() if self.title_case else text,
            font=self.font,
            text_color=self.text_color,
            text_hover=self.text_hover,
            active_offset=self.active_offset,
        )
        button.action = action
        self.buttons.append(button)
        self._sync_focus()
        return button

    def select_next(self) -> None:
        """Select the next button, wrapping around at the end."""
        self._move(1)

    def select_previous(self) -> None:
        """Select the previous button, wrapping around at the start."""
        self._move(-1)

    def handle_event(self, event: Any) -> bool:
        """
        Process a pygame event.

        Keyboard: Up/Down change the selection; Enter presses the
        selected button on key down and triggers its action on key up
        (mirroring a mouse click). Mouse: moving over a button selects
        it, and clicking it triggers its action.

        Parameters
        ----------
        event : pygame.event.Event
            Event to process.

        Returns
        -------
        bool
            True if the event was valid for this menu (navigation, press
            or trigger), False if it was ignored.

        Notes
        -----
        An action may replace the menu (e.g. to change screens), so no
        button is touched after an action runs.
        """
        if not self.buttons:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.select_previous()
                return True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.select_next()
                return True
            if event.key in ENTER_KEYS:
                self.buttons[self.selected].press()
                return True
            return False

        if event.type == pygame.KEYUP and event.key in ENTER_KEYS:
            button = self.buttons[self.selected]
            if button.is_active:
                button.release()
                button.action()     # ! Kill Mypy bitte
                return True
            return False

        if event.type == pygame.MOUSEMOTION:
            return self.hover(event.pos)

        for button in self.buttons:
            if button.handle_event(event):
                button.action()
                return True
        return False

    def hover(self, mouse_pos: Any) -> bool:
        """
        Select the button under the mouse cursor, if any.

        Parameters
        ----------
        mouse_pos : tuple of int
            Mouse position ``(x, y)``.

        Returns
        -------
        bool
            True if the cursor is over a button, False otherwise.
        """
        for index, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.selected = index
                self._sync_focus()
                return True
        return False

    def draw(self, surface: Any) -> None:
        """
        Draw every button.

        Parameters
        ----------
        surface : pygame.Surface
            Surface to draw on.
        """
        for button in self.buttons:
            button.draw(surface)

    # Makes Menu behave like a list[Button]
    def __iter__(self) -> Iterator[Button]:
        return iter(self.buttons)

    def __len__(self) -> int:
        return len(self.buttons)

    # ------------------------------------------------------------------
    def _move(self, step: int) -> None:
        """Move the selection by `step` positions, with wrap-around."""
        if self.buttons:
            self.selected = (self.selected + step) % len(self.buttons)
            self._sync_focus()

    def _sync_focus(self) -> None:
        """Highlight only the selected button."""
        for index, button in enumerate(self.buttons):
            button.is_hovered = index == self.selected
