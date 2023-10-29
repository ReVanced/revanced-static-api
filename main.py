from genericpath import isdir, isfile
import os
import shutil
from app.config import load_config
from app.generator import DefaultGeneratorProvider

config = load_config()

output = config["output"] if "output" in config else "static"
purge = config["purge"] if "purge" in config else []
generator_configs = config["configs"]

generator_provider = DefaultGeneratorProvider()

for path in purge:
    if isdir(path):
        shutil.rmtree(path)
    elif isfile(path):
        os.remove(path)

for config in generator_configs:
    for generator_name in config["generators"]:
        generator = generator_provider.get(generator_name)
        if generator is None:
            continue
        generator.generate(config, output)
