from decimal import Decimal
import strawberry
from strawberry.asgi import GraphQL
from mangum import Mangum
from lib import dynamodb as db
from lib import opus
from enum import StrEnum, auto


@strawberry.enum
class Kind(StrEnum):
    composer = auto()
    collection = auto()
    song = auto()


@strawberry.interface
class Record:
    """This name is mega generic but hey"""

    pk: strawberry.Private[str]
    sk: strawberry.Private[str]

    name: str

    # not sure whether this is nice or not
    # basically, having these here allows to construct
    # the records directly form searches. Explicit would
    # probably be better
    search_name: strawberry.Private[str | None] = None
    random: strawberry.Private[Decimal | None] = None

    @strawberry.field
    def id(self) -> int:
        return int(self.sk.split(":")[1])


@strawberry.type
class Song(Record):
    # this being optional is only needed to facilitate searching.
    # should add `tones` to the index projection in dynamo instead
    tones: str | None = None

    @strawberry.field
    def opus(self) -> str:
        return resolve_opus(self.tones)


@strawberry.interface
class Group:
    @strawberry.field
    def songs(self) -> list[Song]:
        songs = db.memberships(self.sk)

        return [Song(**song) for song in songs]


@strawberry.type
class Composer(Record, Group):
    first_name: str | None = None
    last_name: str

    @classmethod
    def from_searchresult(cls, data: dict):
        last, _, first = data["name"].partition(", ")

        return cls(**data, last_name=last, first_name=first or None)


@strawberry.type
class Collection(Record, Group):
    pass


def get_one_of_kind(kind: db.Kind, id: int):
    sk = f"{kind}:{id}"
    return db.get_item(kind, sk)


def get_song(id: int) -> Song:
    return Song(**get_one_of_kind(db.Kind.song, id))


def get_composer(id: int) -> Composer:
    return Composer(**get_one_of_kind(db.Kind.composer, id))


def get_collection(id: int) -> Collection:
    return Collection(**get_one_of_kind(db.Kind.collection, id))


def resolve_opus(tones: str):
    data = opus.get(tones)
    return data["opus"].value.decode("utf-8")


@strawberry.type
class Query:

    opus: str = strawberry.field(resolver=resolve_opus)
    song: Song = strawberry.field(resolver=get_song)
    composer: Composer = strawberry.field(resolver=get_composer)
    collection: Collection = strawberry.field(resolver=get_collection)

    @strawberry.field
    def random_song(self) -> Song:
        item = db.random(db.Kind.song)

        return Song(**item)

    @strawberry.field
    def search(self, kind: Kind, string: str) -> list[Record]:
        if not string:
            # `kind` is technically of the wrong type for db.list_kind
            records = sorted(db.list_kind(kind), key=lambda x: x["name"])

        else:
            records = db.search(kind, string)

            # a bit janky to do this here, but oh well
            if kind == Kind.composer:
                return [Composer.from_searchresult(record) for record in records]

        mapping = {
            Kind.song: Song,
            Kind.composer: Composer,
            Kind.collection: Collection,
        }

        model = mapping[kind]

        return [model(**record) for record in records]


schema = strawberry.Schema(query=Query)
app = GraphQL(schema)
handler = Mangum(app)
