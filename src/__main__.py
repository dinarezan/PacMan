import json
import hjson
from src.entities.file_loaders import load_config
from pydantic import ValidationError
from src.core.engine import Engine

CONFIG_PATH = "config.hjson"


if __name__ == "__main__":
    try:
        config = load_config(CONFIG_PATH)

        engine = Engine(config)
        engine.run()

    except FileNotFoundError as e:
        print("FileNotFoundError:", e)
    except json.JSONDecodeError as e:
        print("JSONDecodeError caught:", e)
    except hjson.HjsonDecodeError as e:
            print("HJSONDecodeError caught:", e)
    except ValidationError as e:
        print(f"Validation error caught: {e.error_count()} error(s)")
        for error in e.errors():
            attr = error['loc']
            print(f"{attr[0]}: {error['msg']} [{error['type']}]")
    except TypeError as e:
        print("TypeError caught:", e)
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print("Unexpected error occured:", e)
