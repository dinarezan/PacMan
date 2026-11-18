import json
import os
from .models import Game
from .player import Highscores, Player
from pathlib import Path

TEMP_SCORE = "data/temp/score.txt"


def load_highscores(path: str) -> Highscores:
    file_path = Path(path)
    if file_path.exists():
        with open(file_path, 'r', encoding="utf-8") as f:
            highscores = json.load(f)
        return Highscores(players=highscores["players"])
    else:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            pass
        return Highscores(players=[])


def load_config(path: str) -> Game:
    with open(path, 'r') as f:
        config = json.load(f)
    game = Game(**config)
    return game



def save_highscore(path: str, name: str, score: int) -> None:
    pass

 # ! PACMAN doesn't like tempo files :(
def load_temp_score() -> int:
    file_path = Path(TEMP_SCORE)
    if file_path.exists():
        with open(file_path, 'r') as f:
            return int(f.read())
    else:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write("0")
        return 0


def update_temp_score(score: int) -> None:
    with open(TEMP_SCORE, 'w') as f:
        f.write(str(score))


def delete_temp_score() -> None:
    file_path = Path(TEMP_SCORE)
    os.remove(TEMP_SCORE)
    os.rmdir(file_path.parent)
