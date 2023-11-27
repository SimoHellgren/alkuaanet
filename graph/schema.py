import strawberry
from strawberry.asgi import GraphQL
import crud
from mangum import Mangum
from typing import Optional


@strawberry.type
class SearchResult:
    id: str
    name: str

    @classmethod
    def from_db(cls, record):
        return cls(id=record["pk"], name=record["name"])


@strawberry.type
class Song:
    id: str
    name: str
    tones: str
    opus: str


@strawberry.input
class ComposerInput:
    first_name: str
    last_name: str

    def to_dict(self):
        return {"first_name": self.first_name, "last_name": self.last_name}


@strawberry.input
class SongInput:
    name: str
    tones: str
    composer: Optional[ComposerInput] = None
    collections: Optional[list[str]] = None


def search(kind: str, string: str) -> list[SearchResult]:
    data = crud.search(kind, f"name:{string.lower()}")
    return [SearchResult.from_db(datum) for datum in data]


def get_items(pk: str, sk: str):
    data = crud.get_by_pk(pk, sk)
    return [SearchResult(id=datum["sk"], name=datum["name"]) for datum in data]


def get_song(song_id: str):
    data = crud.get_by_pk(song_id, "name")[0]
    opus = crud.get_opus(data["tones"])
    return Song(
        id=data["pk"],
        name=data["name"],
        tones=data["tones"],
        opus=opus,
    )


@strawberry.type
class Query:
    song: Song = strawberry.field(resolver=get_song)
    item: list[SearchResult] = strawberry.field(resolver=get_items)
    search: list[SearchResult] = strawberry.field(resolver=search)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_song(self, song: SongInput) -> None:
        crud.create_song(
            song.name,
            song.tones,
            song.composer.to_dict(),
            song.collections,
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)

app = GraphQL(schema)
handler = Mangum(app)
