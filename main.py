import click

from commands.generate import generate


@click.group()
def main():
    pass


main.add_command(generate)

if __name__ == "__main__":
    main()
