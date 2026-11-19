from .entities import load_config, load_highscores
import json
from pydantic import ValidationError
from src.core.engine import Engine
from .entities import Player

CONFIG_PATH = "config.json"



if __name__ == "__main__":
    config = load_config(CONFIG_PATH)

    engine = Engine(config)
    engine.run()

    


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
