from enum import Enum


class Colors(Enum):
    RED = 'red'
    PINK = 'pink'
    ORANGE = 'orange'
    CYAN = 'cyan'
    PURPLE = 'purple'
    PEACH = 'peach'
    GREEN = 'green'
    GREY = 'grey'
    YELLOW = 'yellow'
    BLUE = 'blue'
    BLACK = 'black'


FRUITS: dict


# Hue is in degrees; saturation and luminosity are percentage changes.
GHOST_COLOR_ADJUSTMENTS: dict[Colors, tuple[int, int, int]] = {
    Colors.ORANGE: (29, -11, 0),
    Colors.CYAN: (-180, -18, 0),
    Colors.YELLOW: (52, -10, 0),
    Colors.GREEN: (100, -36, 0),
    Colors.PURPLE: (-85, -68, 0),
    Colors.PINK: (-40, -40, 10),
    Colors.PEACH: (9, -26, 0),
    Colors.GREY: (0, -100, 0),
}


class States(Enum):
    START = 'start'
    END = 'end'
    GAME = 'game'
    PAUSE = 'pause'
    LOSE = 'lose'
    WIN = 'win'
