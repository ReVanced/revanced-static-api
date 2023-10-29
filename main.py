from app.config import load_config
from app.generator import DefaultGeneratorProvider

config = load_config()

output = config["output"]
configs = config["configs"]

generator_provider = DefaultGeneratorProvider()

for config in configs:
    for generator_name in config["generators"]:
        generator = generator_provider.get(generator_name)
        if generator is None:
            continue
        generator.generate(config, output)
