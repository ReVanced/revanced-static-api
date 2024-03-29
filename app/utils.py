import json
import os


def write_json(text: str | dict | list, to, overwrite=True):
    if not os.path.exists(to) or overwrite:
        with open(to, "w") as f:
            text = to_json(text)
            f.write(text)

def to_json(text: str | dict | list):
    if not isinstance(text, str):
        text = json.dumps(text, indent=2)
    return text

def read_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def create_if_not_exists(path):
    os.makedirs(path, exist_ok=True)


def get_repository_name(repository: str):
    return repository.split("/")[-1]
