import strawberry
from strawberry.asgi import GraphQL
import boto3
from lib import crud2 as crud
from lib import models
from enum import StrEnum, auto

TABLE = boto3.resource("dynamodb").Table("songs_v2")


@strawberry.enum
class Kind(StrEnum):
    composer = auto()
    collection = auto()
    song = auto()


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

    @classmethod
    def from_db(cls, record: models.Song):
        return cls(
            id=sk_to_id(record.sk),
            name=record.name,
            tones=record.tones,
        )

    @classmethod
    def from_searchresult(cls, record: models.SearchResult):
        return cls(
            id=sk_to_id(record.sk),
            name=record.name,
            tones=record.tones,
        )


def get_song(id: int) -> Song:
    song = crud.songs.get(TABLE, id)

    return Song.from_db(song)


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
        return [Song.from_db(record) for record in records]

    @classmethod
    def from_searchresult(cls, record: models.SearchResult):
        last, first = record.name.split(", ", maxsplit=1)

        return cls(id=sk_to_id(record.sk), first_name=first, last_name=last)


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
        records = crud.composers.list_songs(TABLE, self.id)
        return [Song.from_db(record) for record in records]

    @classmethod
    def from_searchresult(cls, record: models.SearchResult):
        return cls(
            id=sk_to_id(record.sk),
            name=record.name,
        )


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
    def search(self, kind: Kind, string: str) -> list[Song | Composer | Collection]:
        mapping = {
            Kind.song: (crud.songs, Song),
            Kind.collection: (crud.collections, Collection),
            Kind.composer: (crud.composers, Composer),
        }

        searcher, model = mapping[kind]

        records = searcher.search(TABLE, string)
        return [model.from_searchresult(record) for record in records]


schema = strawberry.Schema(query=Query)
app = GraphQL(schema)
