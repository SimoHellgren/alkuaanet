import strawberry
from strawberry.asgi import GraphQL
import crud
from mangum import Mangum


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


def search(kind: str, string: str) -> list[SearchResult]:
    data = crud.search(kind, f"name:{string}")["Items"]
    return [SearchResult.from_db(datum) for datum in data]


def get_song(song_id: str):
    data = crud.get_by_pk(song_id)["Items"][0]
    return Song(
        id=data["pk"],
        name=data["name"],
        tones=data["tones"],
        opus=data["opus"].value.decode("utf-8"),
    )


@strawberry.type
class Query:
    song: Song = strawberry.field(resolver=get_song)
    search: list[SearchResult] = strawberry.field(resolver=search)


schema = strawberry.Schema(query=Query)

app = GraphQL(schema)
handler = Mangum(app)
