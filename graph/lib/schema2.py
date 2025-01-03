import strawberry
from strawberry.asgi import GraphQL
import boto3
from lib import crud2 as crud
from lib import models

TABLE = boto3.resource("dynamodb").Table("songs_v2")


@strawberry.experimental.pydantic.type(model=models.SearchResult, all_fields=True)
class SearchResult:
    """This might be an unnecessary abstraction in the API:
    Ideally, the user would never need to deal with this internal detail.
    """


def resolve_opus(tones: str):
    obj = crud.opus.get(TABLE, tones)
    return obj.opus.value.decode("utf-8")


@strawberry.experimental.pydantic.type(model=models.Song, all_fields=True)
class Song:

    @strawberry.field
    def opus(self) -> str:
        return resolve_opus(self.tones)


@strawberry.experimental.pydantic.type(model=models.Composer, all_fields=True)
class Composer:

    # this is already defined in the pydantic model, but for some reason it's not picked up
    @strawberry.field
    def name(self) -> str:
        return f"{self.last_name}, {self.first_name}"

    @strawberry.field
    def songs(self) -> list[SearchResult]:
        _, num = self.sk.split(":")  # ugly
        return crud.composers.list_songs(TABLE, int(num))


@strawberry.experimental.pydantic.type(model=models.Collection, all_fields=True)
class Collection:
    @strawberry.field
    def songs(self) -> list[SearchResult]:
        _, num = self.sk.split(":")  # ugly
        return crud.collections.list_songs(TABLE, int(num))


@strawberry.type
class Query:

    opus: str = strawberry.field(resolver=resolve_opus)

    @strawberry.field
    def song(self, id: int) -> Song:
        return crud.songs.get(TABLE, id)

    @strawberry.field
    def search_song(self, string: str) -> list[SearchResult]:
        return crud.songs.search(TABLE, string)

    @strawberry.field
    def composer(self, id: int) -> Composer:
        return crud.composers.get(TABLE, id)

    @strawberry.field
    def search_composer(self, string: str) -> list[SearchResult]:
        return crud.composerss.search(TABLE, string)

    @strawberry.field
    def collection(self, id: int) -> Collection:
        return crud.collections.get(TABLE, id)

    @strawberry.field
    def search_collection(self, string: str) -> list[SearchResult]:
        return crud.collections.search(TABLE, string)


schema = strawberry.Schema(query=Query)
app = GraphQL(schema)
