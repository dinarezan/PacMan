from entities import Map, load_config
import json
from pydantic import ValidationError
from game import Game


CONFIG_PATH = "config.json"


if __name__ == "__main__":
    try:
        config = load_config(CONFIG_PATH)

        game = Game(config)
        game.run()
        #Game(config={}).run()


        #while game.levels:
        #    level = game.levels.pop(0)
        #    map = Map(size=(level.width, level.height), seed=level.seed, ghosts=level.ghosts,
        #            pacgum=level.pacgum, max_time=level.max_time)
            # print("level:\n", map.maze)

    except FileNotFoundError as e:
        print("FileNotFoundError:", e)
    except json.JSONDecodeError as e:
        print("JSONDecodeError caught:", e)
    except ValidationError as e:
        print(f"Validation error caught: {e.error_count()} error(s)")
        for error in e.errors():
            attr = error['loc']
            print(f"{attr[0]}: {error['msg']} [{error['type']}]")
    except TypeError as e:
        print("TypeError caught:", e)
    except Exception as e:
        print("Unexpected error occured:", e)
