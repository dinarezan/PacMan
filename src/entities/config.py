import json
from .models import Game
from pydantic import ValidationError


def load_config(path: str) -> Game:
    # try:
        with open(path, 'r') as f:
            config = json.load(f)
        game = Game(**config)
        return game
    # except FileNotFoundError as e:
    #     raise FileNotFoundError from e
    # except json.JSONDecodeError as e:
    #     raise json.JSONDecodeError from e
    # except ValidationError as e:
    #     raise ValidationError from e
