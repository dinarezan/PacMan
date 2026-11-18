from .entities import load_config, load_highscores
import json
from pydantic import ValidationError
from src.core.engine import Engine
from .entities import Player

CONFIG_PATH = "config.json"
HIGHSCORE_PATH = "data/highscores.json"


if __name__ == "__main__":
    config = load_config(CONFIG_PATH)
    highscores = load_highscores(HIGHSCORE_PATH)

    name = input("Player name: ")
    player = Player(name=name)  # validates the name (min 5 chars)

    engine = Engine(config)
    engine.run()
    score = engine.score

    existing: Player = next((p for p in highscores.players if p.name == player.name), None)
    if existing is None:
        highscores.players.append(Player(name=player.name, score=score))
    elif score > existing.score:
        existing.score = score

    highscores.players.sort(key=lambda p: p.score, reverse=True)

    with open(HIGHSCORE_PATH, "w") as f:
        f.write(highscores.model_dump_json(indent=2))
    


    # except FileNotFoundError as e:
    #     print("FileNotFoundError:", e)
    # except json.JSONDecodeError as e:
    #     print("JSONDecodeError caught:", e)
    # except ValidationError as e:
    #     print(f"Validation error caught: {e.error_count()} error(s)")
    #     for error in e.errors():
    #         attr = error['loc']
    #         print(f"{attr[0]}: {error['msg']} [{error['type']}]")
    # except TypeError as e:
    #     print("TypeError caught:", e)
    # except Exception as e:
    #     print("Unexpected error occured:", e)
