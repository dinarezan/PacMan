import json
from .models import Game, Highscores, Player
from pathlib import Path

TEMP_SCORE = "data/temp/score.txt"
HIGHSCORE_PATH = "data/highscores.json"


def load_highscores() -> Highscores:
    file_path = Path(HIGHSCORE_PATH)
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



def save_highscore(name: str, score: int) -> None:
    highscores = load_highscores(HIGHSCORE_PATH)
    player = name
    Player(name=player)

    existing: Player = next((p for p in highscores.players if p.name == player.name), None)
    if existing is None:
        highscores.players.append(Player(name=player.name, score=score))
    elif score > existing.score:
        existing.score = score

    highscores.players.sort(key=lambda p: p.score, reverse=True)

    with open(HIGHSCORE_PATH, "w") as f:
        f.write(highscores.model_dump_json(indent=2))


 # ! PACMAN doesn't like tempo files :(
# def load_temp_score() -> int:
#     file_path = Path(TEMP_SCORE)
#     if file_path.exists():
#         with open(file_path, 'r') as f:
#             return int(f.read())
#     else:
#         file_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(file_path, 'w') as f:
#             f.write("0")
#         return 0


# def update_temp_score(score: int) -> None:
#     with open(TEMP_SCORE, 'w') as f:
#         f.write(str(score))


# def delete_temp_score() -> None:
#     file_path = Path(TEMP_SCORE)
#     os.remove(TEMP_SCORE)
#     os.rmdir(file_path.parent)
