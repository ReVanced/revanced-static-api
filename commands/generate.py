import asyncio
from genericpath import isdir, isfile
import os
import shutil

import click
from app.config import load_config
from app.dependencies import wire_dependencies
from app.generator import get_generators
from app.utils import create_if_not_exists


@click.group()
def generator():
    pass


@click.command()
def generate():
    config = load_config()

    wire_dependencies()

    purge(config["purge"])

    generators = get_generators()

    loop = asyncio.get_event_loop()
    tasks = []

    output = config["output"]
    create_if_not_exists(output)

    for generator_config in config["configs"]:
        for generator_name in generator_config["generators"]:
            generator = generators[generator_name] if generator_name in generators else None

            tasks.append(
                loop.create_task(generator.generate(generator_config, output))
            ) if generator is not None else print(f"Generator {generator_name} not found.")

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


def purge(paths):
    for path in paths:
        if isdir(path):
            shutil.rmtree(path)
        elif isfile(path):
            os.remove(path)


generator.add_command(generate)
