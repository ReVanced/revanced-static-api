import json
import os


def write_json(text: str | dict | list, to: str, overwrite: bool = True):
    if not os.path.exists(to) or overwrite:
        with open(to, "w") as f:
            if not isinstance(text, str):
                text = json.dumps(text)
            f.write(text)


def read_json(path: str, default: list) -> list:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def create_if_not_exists(path: str):
    os.makedirs(path, exist_ok=True)


def get_repository_name(repository: str) -> str:
    return repository.split("/")[-1]
