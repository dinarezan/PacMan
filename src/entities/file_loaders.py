import hjson
import json
from .models import Game, Highscores, Player
from pathlib import Path

HIGHSCORE_PATH = "data/highscores.json"


def load_highscores(path: str) -> Highscores:
    file_path = Path(path or HIGHSCORE_PATH)

    if file_path.exists():
        with open(file_path, 'r', encoding="utf-8") as f:
            highscores = json.load(f)
        return Highscores.model_validate(highscores)
    else:
        return Highscores(players=[])


def save_highscore(path: str, name: str, score: int) -> None:
    file_path = Path(path or HIGHSCORE_PATH)

    player = Player(name=name.strip(), score=score)
    highscores = load_highscores(path)
    existing = next((p for p in highscores.players
                     if p.name == player.name), None)
    if existing is None:
        highscores.players.append(player)
    elif player.score > existing.score:
        existing.score = player.score

    highscores.players.sort(key=lambda p: p.score, reverse=True)

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(highscores.model_dump_json(indent=2),
                         encoding="utf-8")


def load_config(path: str) -> Game:
    with open(path, 'r') as f:
        config = hjson.load(f)
    game = Game(**config)
    return game
