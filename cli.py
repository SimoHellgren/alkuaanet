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


@song.command(name="get")
@click.argument("id", type=click.INT)
def get_song(id: int):
    result = crud.get_by_pk(f"song:{id}", "name")
    if result:
        print(result[0])


if __name__ == "__main__":
    cli()
