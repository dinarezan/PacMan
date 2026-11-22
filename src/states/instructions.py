
from __future__ import annotations

from pathlib import Path
from typing import Any

import pygame

# (keys, description)  # ?? Optional add key for cheats or input chat
CONTROLS = [
    ("Arrow keys / W A S D", "Move Pac-Man up, down, left and right."),
    ("Shift", "Dash at 10x speed and ignore ghosts for 0.8 seconds (15s cooldown)."),
    ("Enter", "Select the highlighted menu option."),
    ("Up / Down", "Move through the menu options or scroll a screen."),
    ("A / S", "Move through the menu options or scroll a screen."),
    ("Backspace", "Go back to the previous menu."),
    ("P / Esc / Space", "Pause or resume the game."),
    ("M", "Mute or unmute the sound."),
]

# (image file, name, description)  # TODO Add/edit new elements here
ELEMENTS = [
    ("pacman.png", "Pac-Man",
     "The main one! Guide him through the maze with the arrow keys."),
    ("pac-dots.png", "Pac-Dots",
     "Eat every dot in the maze to clear the level."),
    ("power-pellets.png", "Dina's food",
     "Eat one and the ghosts turn blue and run away for a short time."),
    ("ghost.png", "Ghosts",
     "Avoid them! If a ghost catches you, you lose a life."),
    ("frightered-ghost.png", "Frightened Ghosts",
     "While a ghost is blue you can eat it for bonus points."),
    ("fruit.png", "Fruit",
     "Bonus fruit appears from time to time. Grab it for extra points."),
    ("power-up.png", "Power-Up",
     "A hot coffee gives Pac-Man a short boost of speed."),
]

GOAL = ("Eat all the pac-dots in the maze while dodging the ghosts. "
        "Clear every dot to move on to the next level.")


class Instructions:
    """
    Vertically scrollable "how to play" screen.

    The whole content is rendered once on a tall surface; drawing only
    blits the visible slice, so scrolling is cheap.

    Parameters
    ----------
    viewport : pygame.Rect
        Screen area where the content is shown.
    font : pygame.font.Font
        Font used for section headings.
    assets_dir : pathlib.Path
        Folder containing the images listed in `ELEMENTS`.

    Attributes
    ----------
    viewport : pygame.Rect
        Screen area where the content is shown.
    content : pygame.Surface
        Pre-rendered content (taller than the viewport when scrollable).
    offset : int
        Current vertical scroll, in pixels.
    max_offset : int
        Largest allowed scroll value.
    """

    SCROLL_SPEED = 8        # pixels per frame while a key is held
    WHEEL_STEP = 40         # pixels per mouse-wheel notch
    PAGE_STEP = 300         # pixels for Page Up / Page Down
    SCROLLBAR_WIDTH = 6
    IMAGE_SIZE = (50, 50)
    KEY_COL_WIDTH = 140
    GAP = 16

    HEADING_COLOR = (0, 220, 0)
    KEY_COLOR = (255, 0, 0)
    TEXT_COLOR = (200, 200, 200)

    def __init__(self, viewport: pygame.Rect, font: Any,
                 assets_dir: Path) -> None:
        self.viewport = pygame.Rect(viewport)
        self.heading_font = font
        self.body_font = pygame.font.Font(None, 24)
        self.assets_dir = Path(assets_dir)
        self.offset = 0
        # Leave room for the scrollbar on the right.
        self.content_width = self.viewport.width - self.SCROLLBAR_WIDTH - 8
        self.content = self._build_content()
        self.max_offset = max(0, self.content.get_height()
                              - self.viewport.height)

    # ---- content -----------------------------------------------------
    def _load_image(self, name: str) -> pygame.Surface:
        """Load an image, or return a placeholder if it can't be read."""
        try:
            image = pygame.image.load(str(self.assets_dir / 'icons' / name))
            return pygame.transform.smoothscale(
                image.convert_alpha(), self.IMAGE_SIZE)
        except (pygame.error, FileNotFoundError):
            print("Failure to load icons images in Instructions")
            placeholder = pygame.Surface(self.IMAGE_SIZE, pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (90, 90, 90),
                             placeholder.get_rect(), width=2)
            return placeholder

    def _wrap(self, text: str, font: Any, color: tuple[int, int, int],
              width: int) -> pygame.Surface:
        """Render `text` word-wrapped to `width` pixels."""
        lines: list[str] = []
        line = ""
        for word in text.split():
            candidate = f"{line} {word}".strip()
            if font.size(candidate)[0] <= width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)

        step = font.get_linesize()
        surface = pygame.Surface((width, max(step, step * len(lines))),
                                 pygame.SRCALPHA)
        for index, text_line in enumerate(lines):
            surface.blit(font.render(text_line, True, color),
                         (0, index * step))
        return surface

    def _build_content(self) -> pygame.Surface:
        """Lay out every block, then render them on one tall surface."""
        blocks: list[tuple[pygame.Surface, int, int]] = []
        y = 0
        width = self.content_width

        def add_heading(text: str) -> None:
            nonlocal y
            surface = self.heading_font.render(text, True,
                                               self.HEADING_COLOR)
            blocks.append((surface, 0, y))
            y += surface.get_height() + 10

        def add_row(left: pygame.Surface, right: pygame.Surface,
                    right_x: int) -> None:
            nonlocal y
            blocks.append((left, 0, y))
            blocks.append((right, right_x, y))
            y += max(left.get_height(), right.get_height()) + 14

        add_heading("Goal")
        goal = self._wrap(GOAL, self.body_font, self.TEXT_COLOR, width)
        blocks.append((goal, 0, y))
        y += goal.get_height() + 24

        add_heading("Controls")
        right_x = self.KEY_COL_WIDTH + self.GAP
        for keys, description in CONTROLS:
            add_row(
                self._wrap(keys, self.body_font, self.KEY_COLOR,
                           self.KEY_COL_WIDTH),
                self._wrap(description, self.body_font, self.TEXT_COLOR,
                           width - right_x),
                right_x,
            )
        y += 10

        add_heading("How to play")
        right_x = self.IMAGE_SIZE[0] + self.GAP
        for file_name, name, description in ELEMENTS:
            title = self.body_font.render(name, True, self.KEY_COLOR)
            text = self._wrap(description, self.body_font, self.TEXT_COLOR,
                              width - right_x)
            label = pygame.Surface(
                (width - right_x, title.get_height() + 2
                 + text.get_height()), pygame.SRCALPHA)
            label.blit(title, (0, 0))
            label.blit(text, (0, title.get_height() + 2))
            add_row(self._load_image(file_name), label, right_x)

        content = pygame.Surface((width, max(y, 1)), pygame.SRCALPHA)
        for surface, x, block_y in blocks:
            content.blit(surface, (x, block_y))
        return content

    # ---- scrolling ---------------------------------------------------
    def reset(self) -> None:
        """Scroll back to the top."""
        self.offset = 0

    def scroll_by(self, dy: int) -> None:
        """Scroll by `dy` pixels (positive is down), clamped to range."""
        self.offset = max(0, min(self.max_offset, self.offset + dy))

    def handle_event(self, event: Any) -> bool:
        """
        Process a scroll-related event.

        Holding Up/Down is handled smoothly in `update`; here those keys
        are only consumed so the menu does not react to them.

        Returns
        -------
        bool
            True if the event was consumed, False otherwise.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.scroll_by(-100)
                return True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll_by(100)
                return True
            if event.key == pygame.K_PAGEUP:
                self.scroll_by(-self.PAGE_STEP)
                return True
            if event.key == pygame.K_PAGEDOWN:
                self.scroll_by(self.PAGE_STEP)
                return True
            if event.key == pygame.K_HOME:
                self.offset = 0
                return True
            if event.key == pygame.K_END:
                self.offset = self.max_offset
                return True
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_by(-event.y * self.WHEEL_STEP)
            return True
        return False

    def update(self) -> None:
        """Scroll continuously while Up or Down is held."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.scroll_by(-self.SCROLL_SPEED)
        if keys[pygame.K_DOWN]:
            self.scroll_by(self.SCROLL_SPEED)

    # ---- drawing -----------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the visible slice of the content and the scrollbar."""
        area = pygame.Rect(0, self.offset, self.content.get_width(),
                           self.viewport.height)
        surface.blit(self.content, self.viewport.topleft, area)

        if self.max_offset > 0:
            track = pygame.Rect(
                self.viewport.right - self.SCROLLBAR_WIDTH,
                self.viewport.top, self.SCROLLBAR_WIDTH,
                self.viewport.height)
            pygame.draw.rect(surface, (40, 40, 40), track, border_radius=3)

            thumb_height = max(
                24, track.height * self.viewport.height
                // self.content.get_height())
            travel = track.height - thumb_height
            thumb_y = track.top + travel * self.offset // self.max_offset
            thumb = pygame.Rect(track.left, thumb_y, track.width,
                                thumb_height)
            pygame.draw.rect(surface, (0, 200, 0), thumb, border_radius=3)
