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


def sk_to_id(sk: str) -> int:
    return int(sk.split(":")[1])


@strawberry.type
class Song:
    id: int
    name: str
    tones: str

    @strawberry.field
    def opus(self) -> str:
        return resolve_opus(self.tones)


def get_song(id: int) -> Song:
    song = crud.songs.get(TABLE, id)

    return Song(
        id=sk_to_id(song.sk),
        name=song.name,
        tones=song.tones,
    )


@strawberry.type
class Composer:
    id: int
    first_name: str
    last_name: str

    # this is already defined in the pydantic model, but for some reason it's not picked up
    @strawberry.field
    def name(self) -> str:
        return f"{self.last_name}, {self.first_name}"

    @strawberry.field
    def songs(self) -> list[Song]:
        records = crud.composers.list_songs(TABLE, self.id)
        return [get_song(sk_to_id(record.sk)) for record in records]


def get_composer(id: int) -> Composer:
    composer = crud.composers.get(TABLE, id)

    return Composer(
        id=sk_to_id(composer.sk),
        first_name=composer.first_name,
        last_name=composer.last_name,
    )


@strawberry.type
class Collection:
    id: int
    name: str

    @strawberry.field
    def songs(self) -> list[Song]:
        records = crud.collections.list_songs(TABLE, self.id)
        return [get_song(sk_to_id(record.sk)) for record in records]


def get_collection(id: int) -> Collection:
    collection = crud.collections.get(TABLE, id)

    return Collection(
        id=sk_to_id(collection.sk),
        name=collection.name,
    )


@strawberry.type
class Query:

    opus: str = strawberry.field(resolver=resolve_opus)
    song: Song = strawberry.field(resolver=get_song)
    composer: Composer = strawberry.field(resolver=get_composer)
    collection: Collection = strawberry.field(resolver=get_collection)

    @strawberry.field
    def search_song(self, string: str) -> list[SearchResult]:
        return crud.songs.search(TABLE, string)

    @strawberry.field
    def search_composer(self, string: str) -> list[SearchResult]:
        return crud.composers.search(TABLE, string)

    @strawberry.field
    def search_collection(self, string: str) -> list[SearchResult]:
        return crud.collections.search(TABLE, string)


schema = strawberry.Schema(query=Query)
app = GraphQL(schema)
