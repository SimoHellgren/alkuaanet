import strawberry
from strawberry.asgi import GraphQL
import crud
from mangum import Mangum


@strawberry.type
class Song:
    id: str
    name: str


def get_songs() -> list[Song]:
    data = crud.get_songs()["Items"]
    return [Song(id=song["pk"], name=song["name"]) for song in data]


@strawberry.type
class Query:
    songs: list[Song] = strawberry.field(resolver=get_songs)


schema = strawberry.Schema(query=Query)

app = GraphQL(schema)
handler = Mangum(app)
