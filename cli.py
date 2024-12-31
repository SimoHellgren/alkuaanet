import click
from graph.lib import crud


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


@song.command(name="add")
@click.option("name", "-n", required=True)
@click.option("tones", "-t", required=True, help="e.g. D4-Bb3-F3-Bb2")
@click.option("composer", "-comp", help="Format `Last name,First names`")
@click.option("collections", "-coll", multiple=True)
def add_song(name: str, tones: str, composer: str, collections: list[str]):

    if composer:
        last, _, firsts = [v or None for v in composer.partition(",")]
        composer = {"first_name": firsts, "last_name": last}

    song = crud.create_song(
        name,
        tones,
        composer=composer,
        collections=collections,
    )

    print(song)


if __name__ == "__main__":
    cli()
