import boto3
import click
from lib import crud2 as crud
from lib import models

TABLE = boto3.resource("dynamodb").Table("songs_v2")


@click.group()
def cli():
    pass


@cli.group()
def song():
    pass


@song.command(name="search")
@click.argument("string")
def search_songs(string: str):
    for s in crud.songs.search(TABLE, string):
        print(s)


@song.command(name="get")
@click.argument("id")
def get_song(id: int):
    item = crud.songs.get(TABLE, id)
    print(item)


@song.command(name="create")
@click.option("name", "-n", required=True)
@click.option("tones", "-t", required=True, help="e.g. D4-Bb3-F3-Bb2")
def create_song(name: str, tones: str):
    item_in = models.SongCreate(name=name, tones=tones)

    item = crud.songs.create(TABLE, item_in)

    print(item)


@song.command(name="delete")
@click.argument("id")
def delete_song(id: int):
    items = crud.songs.delete(TABLE, id)

    print("Deleted")
    for item in items:
        print(
            "-", item["Attributes"]
        )  # perhaps should be handled earlier with a proper model


if __name__ == "__main__":
    cli()
