import asyncio
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

    loop = asyncio.get_event_loop()
    tasks = []
    
    for generator_config in config["configs"]:
        for generator_name in generator_config["generators"]:            
            generator = generator_provider.get(generator_name)

            tasks.append(
                loop.create_task(generator.generate(generator_config, output))
            ) if generator is not None else print(f"Generator {generator_name} not found.")
        
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

if __name__ == "__main__":
    wire_dependencies()
    main()
