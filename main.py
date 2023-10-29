from app.config import load_config
from app.generator import DefaultApiProvider

config = load_config()

output = config["output"]
apis = config["api"]

api_provider = DefaultApiProvider()

for api in apis:
    for generator_name in api["generators"]:
        generator = api_provider.get(generator_name)
        if generator is None:
            continue
        generator.generate(api, output)
