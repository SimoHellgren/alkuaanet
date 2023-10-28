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


def get_songs() -> list[SearchResult]:
    data = crud.get_songs()["Items"]
    return [SearchResult.from_db(song) for song in data]


def search_songs(string: str) -> list[SearchResult]:
    data = crud.search_songs(f"name:{string}")["Items"]
    return [SearchResult.from_db(song) for song in data]


def get_song(song_id: str):
    data = crud.get_by_pk(song_id)["Items"][0]
    return Song(
        id=data["pk"],
        name=data["name"],
        tones=data["tones"].value.encode("utf-8"),
        opus=data["opus"],
    )


@strawberry.type
class Query:
    song: Song = strawberry.field(resolver=get_song)
    songs: list[SearchResult] = strawberry.field(resolver=get_songs)
    search: list[SearchResult] = strawberry.field(resolver=search_songs)


schema = strawberry.Schema(query=Query)

app = GraphQL(schema)
handler = Mangum(app)
