import json
from .models import Game
from pydantic import ValidationError


def load_config(path: str) -> Game:
    with open(path, 'r') as f:
        config = json.load(f)
    game = Game(**config)
    return game
