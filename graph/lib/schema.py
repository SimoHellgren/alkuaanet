from decimal import Decimal
import random as rand
import strawberry
from strawberry.asgi import GraphQL
from mangum import Mangum
from lib import crud
from lib.models import Membership
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
    """Would be nice to have a generic implementation, but that
    would probably require a classvar for kind or something
    """

    songs: list[Song]

    @staticmethod
    def _song_from_membership(membership: Membership) -> Song:

        data = {
            **membership.model_dump(),
            "pk": "song",  # override <group>:<id> from membership
        }

        return Song(**data)


@strawberry.type
class Composer(Record, Group):
    first_name: str | None = None
    last_name: str

    @strawberry.field
    def songs(self) -> list[Song]:
        songs = crud.get_composer_songs(self.id())

        return [self._song_from_membership(song) for song in songs]

    @classmethod
    def from_searchresult(cls, data: dict):
        last, _, first = data["name"].partition(", ")

        return cls(**data, last_name=last, first_name=first or None)


@strawberry.type
class Collection(Record, Group):
    @strawberry.field
    def songs(self) -> list[Song]:
        songs = crud.get_collection_songs(self.id())

        return [self._song_from_membership(song) for song in songs]


def get_song(id: int) -> Song:
    obj = crud.read_song(id)
    return Song(**obj.model_dump())


def get_composer(id: int) -> Composer:
    obj = crud.read_composer(id)
    return Composer(**obj.model_dump())


def get_collection(id: int) -> Collection:
    obj = crud.read_collection(id)
    return Collection(**obj.model_dump())


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
        item = crud.get_random_song()

        return Song(**item.model_dump())

    @strawberry.field
    def search(self, kind: Kind, string: str) -> list[Record]:
        if not string:
            # `kind` is technically of the wrong type for db.list_kind
            records = sorted(db.get_partition(kind), key=lambda x: x["name"])

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


@strawberry.input
class SongInput:
    name: str
    tones: str
    composers: list[str] | None = None
    collections: list[str] | None = None


@strawberry.input
class ComposerInput:
    first_name: str | None = None
    last_name: str


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_song(self, song: SongInput) -> Song:
        song_id = db._get_next_id(Kind.song)

        data_in = {
            "pk": "song",
            "sk": f"song:{song_id}",
            "name": song.name,
            "tones": song.tones,
            "search_name": song.name.lower(),
            "random": Decimal(str(rand.random())),
        }

        song_db = db.put(item=data_in)

        return Song(**song_db)

    @strawberry.mutation
    def update_song(
        self, id: int, name: str | None = None, tones: str | None = None
    ) -> Song:

        song = db.get_item(Kind.song, f"{Kind.song}:{id}")

        song["name"] = name or song["name"]
        song["search_name"] = song["name"].lower()
        song["tones"] = tones or song["tones"]  # should check for existing opus here

        new_song = db.put(song)

        return Song(**new_song)

    @strawberry.mutation
    def delete_song(self, id: int) -> int:
        db.delete(pk=Kind.song, sk=f"{Kind.song}:{id}")

        return id

    @strawberry.mutation
    def create_composer(self, composer: ComposerInput) -> Composer:
        composer_id = db._get_next_id(Kind.composer)

        name = composer.last_name + (
            f", {composer.first_name}" if composer.first_name else ""
        )

        data_in = {
            "pk": "composer",
            "sk": f"composer:{composer_id}",
            "name": name,
            "first_name": composer.first_name,
            "last_name": composer.last_name,
            "search_name": name.lower(),
            "random": Decimal(str(rand.random())),
        }

        composer_db = db.put(data_in)

        return Composer(**composer_db)

    @strawberry.mutation
    def update_composer(
        self, id: int, first_name: str | None = None, last_name: str | None = None
    ) -> Composer:
        composer = db.get_item(Kind.composer, f"{Kind.composer}:{id}")

        composer["first_name"] = first_name or composer["first_name"]
        composer["last_name"] = last_name or composer["last_name"]
        composer["name"] = composer["last_name"] + (
            f", {composer['first_name']}" if composer["first_name"] else ""
        )

        composer["search_name"] = composer["name"].lower()

        new_composer = db.put(composer)

        return Composer(**new_composer)

    @strawberry.mutation
    def delete_composer(self, id: int) -> int:
        db.delete(pk=Kind.composer, sk=f"{Kind.composer}:{id}")

        return id

    @strawberry.mutation
    def create_collection(self, name: str) -> Collection:
        collection_id = db._get_next_id(Kind.collection)

        data_in = {
            "pk": Kind.collection,
            "sk": f"{Kind.collection}:{collection_id}",
            "name": name,
            "search_name": name.lower(),
            "random": Decimal(str(rand.random())),
        }

        collection_db = db.put(data_in)

        return Collection(**collection_db)

    @strawberry.mutation
    def update_collection(self, id: int, name: str) -> Collection:
        collection = db.get_item(Kind.collection, f"{Kind.collection}:{id}")

        collection["name"] = name
        collection["search_name"] = name.lower()

        new_collection = db.put(collection)

        return Collection(**new_collection)

    @strawberry.mutation
    def delete_collection(self, id: int) -> int:
        db.delete(pk=Kind.collection, sk=f"{Kind.collection}:{id}")

        return id


schema = strawberry.Schema(query=Query, mutation=Mutation)
app = GraphQL(schema)
handler = Mangum(app)
