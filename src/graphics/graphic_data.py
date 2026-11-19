from enum import Enum


"""
180 Cyan
37 Orange
pink hard ???
"""

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


class States(Enum):
    START = 'start'
    END = 'end'
    GAME = 'game'
    PAUSE = 'pause'
    LOSE = 'lose'
    WIN = 'win'
