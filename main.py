from app.config import load_config
from app.generator import DefaultApiProvider

config = load_config()

output = config["output"]
apis = config["api"]

api_provider = DefaultApiProvider()

for api in apis:
    for type in api["types"]:
        api_type = api_provider.get(type)
        if api_type is None:
            continue
        api_type.generate(api, output)
