import asyncio
from genericpath import isdir, isfile
import os
import shutil
from app.config import load_config
from app.dependencies import wire_dependencies
from app.generator import generators


def main():
    config = load_config()

    purge(config["purge"])

    generate(config)


def generate(config):
    loop = asyncio.get_event_loop()
    tasks = []

    output = config["output"]
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


if __name__ == "__main__":
    wire_dependencies()
    main()
