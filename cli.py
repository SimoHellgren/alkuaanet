import click
from graph import crud


@click.group()
def cli():
    pass


@cli.group()
def song():
    pass


@song.command(name="search")
@click.argument("string")
def search_song(string: str):
    for song in crud.search("song", f"name:{string}"):
        print(song)


if __name__ == "__main__":
    cli()
