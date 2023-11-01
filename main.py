from genericpath import isdir, isfile
import os
import shutil
from app.config import load_config
from app.dependencies import wire_dependencies
from app.generator import DefaultGeneratorProvider

def main():
    config = load_config()

    for path in config["purge"]:
        if isdir(path):
            shutil.rmtree(path)
        elif isfile(path):
            os.remove(path)

    output = config["output"]
    generator_provider = DefaultGeneratorProvider()

    for generator_config in config["configs"]:
        for generator_name in generator_config["generators"]:
            generator = generator_provider.get(generator_name)

            generator.generate(generator_config, output) if generator is not None else print(f"Generator {generator_name} not found.")
if __name__ == "__main__":
    wire_dependencies()
    main()

