import strawberry
from strawberry.asgi import GraphQL
import crud
from mangum import Mangum


@strawberry.type
class Song:
    id: str
    name: str

    @classmethod
    def from_db(cls, record):
        return cls(id=record["pk"], name=record["name"])


def get_songs() -> list[Song]:
    data = crud.get_songs()["Items"]
    return [Song.from_db(song) for song in data]


def search_songs(string: str) -> list[Song]:
    data = crud.search_songs(f"name:{string}")["Items"]
    return [Song.from_db(song) for song in data]


@strawberry.type
class Query:
    songs: list[Song] = strawberry.field(resolver=get_songs)
    search: list[Song] = strawberry.field(resolver=search_songs)


schema = strawberry.Schema(query=Query)

app = GraphQL(schema)
handler = Mangum(app)
