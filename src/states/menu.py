from typing import Any, Callable, Iterator
import pygame

from button import Button  # adjust to where your Button class lives


class Menu:
    """
    Vertical menu of Buttons.

    Creates one `Button` per item and stacks them vertically, starting
    from the given top-left position.

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
        Text color as an RGB tuple while a button is hovered. Default is
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
        Text color while a button is hovered.
    active_offset : tuple of int
        ``(dx, dy)`` shift applied to a button when pressed.
    title_case : bool
        Whether button texts are converted with ``str.title()``.
    buttons : list of Button
        The buttons in the menu, in display order.

    Raises
    ------------------------------------------
    ValueError
        If `items` and `actions` do not have the same length.

    Examples
    ------------------------------------------
    >>> import button
    button of the page.
    """

    def __init__(self,
                 items: list[str],
                 actions: list[Callable[[], None]],
                 x: int,
                 y: int,
                 image_normal: Any,
                 image_active: Any,
                 font: Any = None,
                 spacing: int = 70,
                 text_color: tuple[int, int, int] = (0, 200, 0),
                 text_hover: tuple[int, int, int] = (0, 255, 0),
                 active_offset: tuple[int, int] = (0, 1),
                 title_case: bool = True
                 ) -> None:
        if len(items) != len(actions):
            raise ValueError(
                f"items ({len(items)}) and actions ({len(actions)}) "
                "must have the same length")

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

        for text, action in zip(items, actions):
            self.add_button(text, action)

    # ------------------------------------------------------------------
    def add_button(self, text: str, action: Callable[[], None]) -> Button:
        """ Append a button below the last one and link its action """
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
        return button

    def handle_event(self, event: Any) -> None:
        """ Forward the event to every button and run the clicked action """
        for button in self.buttons:
            if button.handle_event(event):
                button.action()
                # The action may rebuild the menu (change_menu), so stop
                # iterating over buttons that may no longer be valid.
                break

    def hover(self, mouse_pos: Any) -> None:
        for button in self.buttons:
            button.hover(mouse_pos)

    def draw(self, surface: Any) -> None:
        for button in self.buttons:
            button.draw(surface)

    # Makes Menu behave like the old list[Button]
    def __iter__(self) -> Iterator[Button]:
        return iter(self.buttons)

    def __len__(self) -> int:
        return len(self.buttons)


# ----------------------------------------------------------------------
# Usage examples (inside your controller class)
# ----------------------------------------------------------------------
#
# def _make_main_menu(self) -> Menu:
#     return Menu(
#         items=["Maps", "Start", "Exit"],
#         actions=[lambda: self.change_menu('maps'),
#                  self.start_simulation,
#                  self.exit_app],
#         x=self.view.game_width + 46, y=480,
#         image_normal=self.view.normal_button,
#         image_active=self.view.active_button,
#         font=self.view.font,
#     )
#
# def _make_difficult_menu(self) -> Menu:
#     items = ["easy", "medium", "hard", "challenger", "back"]
#     # item=item freezes the current value in each lambda
#     actions = [lambda item=item: self.show_maps(item)
#                for item in items[:-1]]
#     actions.append(lambda: self.change_menu('main'))
#     return Menu(items, actions, x=self.view.game_width + 46, y=480,
#                 image_normal=self.view.normal_button,
#                 image_active=self.view.active_button,
#                 font=self.view.font)
#
# def generate_menu(self, option: str, items: list[str]) -> Menu:
#     files = sorted(items)
#     names = [f.removesuffix(".txt").replace('_', ' ') for f in files]
#     actions = [lambda f=f: self.parse_map(option, f) for f in files]
#     names.append("Back")
#     actions.append(lambda: self.change_menu('maps'))
#     return Menu(names, actions, x=self.view.game_width + 46, y=480,
#                 image_normal=self.view.normal_button,
#                 image_active=self.view.active_button,
#                 font=self.view.font)
#
# Main loop:
#   for event in pygame.event.get():
#       self.menu.handle_event(event)
#   self.menu.draw(self.view.screen)
