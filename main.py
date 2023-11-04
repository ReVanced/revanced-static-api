import click

from commands.announcement import announcement, create
from commands.generate import generator


@click.group()
def main():
    pass


main.add_command(generator)
main.add_command(announcement)

if __name__ == "__main__":
    main()
