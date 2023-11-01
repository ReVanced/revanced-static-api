import json


def load_config() -> dict:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        config["output"] = config["output"] if "output" in config else "static"
        config["purge"] = config["purge"] if "purge" in config else []

        return config

