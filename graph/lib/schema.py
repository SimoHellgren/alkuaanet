from decimal import Decimal
import random as rand
import strawberry
from strawberry.asgi import GraphQL
from mangum import Mangum
from lib import crud
from lib import models
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
    def _song_from_membership(membership: models.Membership) -> Song:

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
    # composers: list[str] | None = None
    # collections: list[str] | None = None


@strawberry.input
class ComposerInput:
    first_name: str | None = None
    last_name: str


@strawberry.input
class CollectionInput:
    name: str


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_song(self, song: SongInput) -> Song:
        songdict = strawberry.asdict(song)
        song_model = models.SongCreate(**songdict)

        db_song = crud.create_song(song_model)

        return Song(**db_song.model_dump())

    @strawberry.mutation
    def update_song(self, id: int, name: str, tones: str) -> Song:
        song_model = models.SongUpdate(
            name=name,
            tones=tones,
        )

        db_song = crud.update_song(id, song_model)

        return Song(**db_song.model_dump())

    @strawberry.mutation
    def delete_song(self, id: int) -> Song:
        db_song = crud.delete_song(id)

        return Song(**db_song.model_dump())

    @strawberry.mutation
    def create_composer(self, composer: ComposerInput) -> Composer:
        composerdict = strawberry.asdict(composer)
        composer_model = models.ComposerCreate(**composerdict)

        db_composer = crud.create_composer(composer_model)

        return Composer(**db_composer.model_dump())

    @strawberry.mutation
    def update_composer(
        self, id: int, first_name: str | None, last_name: str
    ) -> Composer:
        composer_model = models.ComposerUpdate(
            first_name=first_name, last_name=last_name
        )

        db_composer = crud.update_composer(id, composer_model)

        return Composer(**db_composer.model_dump())

    @strawberry.mutation
    def delete_composer(self, id: int) -> Composer:
        db_composer = crud.delete_composer(id)

        return Composer(**db_composer.model_dump())

    @strawberry.mutation
    def create_collection(self, collection: CollectionInput) -> Collection:
        collectiondict = strawberry.asdict(collection)
        collection_model = models.CollectionCreate(**collectiondict)

        db_collection = crud.create_collection(collection_model)

        return Collection(**db_collection.model_dump())

    @strawberry.mutation
    def update_collection(self, id: int, name: str) -> Collection:
        collection_model = models.CollectionUpdate(name=name)

        db_collection = crud.update_collection(id, collection_model)

        return Collection(**db_collection.model_dump())

    @strawberry.mutation
    def delete_collection(self, id: int) -> Collection:
        db_collection = crud.delete_collection(id)
        return Collection(**db_collection.model_dump())


schema = strawberry.Schema(query=Query, mutation=Mutation)
app = GraphQL(schema)
handler = Mangum(app)
