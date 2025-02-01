from decimal import Decimal
import strawberry
from strawberry.asgi import GraphQL
from mangum import Mangum
from lib import crud
from lib import models
from lib import opus
from lib.hankkari import is_hankkari
from enum import StrEnum, auto


@strawberry.enum
class Kind(StrEnum):
    composer = auto()
    collection = auto()
    song = auto()


@strawberry.interface
class Record:
    """This name is mega generic but hey"""

    # private fields not exposed in the API
    pk: strawberry.Private[str]
    sk: strawberry.Private[str]
    # search_name and random are nullable, they are not present in membership
    # records. See Group._song_from_membership for more info.
    search_name: strawberry.Private[str | None]
    random: strawberry.Private[Decimal | None]

    name: str

    @strawberry.field
    def id(self) -> int:
        return int(self.sk.split(":")[1])


@strawberry.type
class Song(Record):
    tones: str

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
        """Construct a Song from a membership record:
        1. override pk (e.g. `composer:1`) with `song`
        2. set search_name and random to null, since they are not needed here
        """
        # search_name and random are used to search and get random records.
        # In the current context, we're listing e.g. a composer's songs, so
        # we don't really need either. If for some reason you'd want to get
        # a random song from a specific group or further search, you can simply
        # filter the membership records, as their number isn't typically that
        # large. If this were to ever become a problem, membership records
        # would probably need to be amended with `random` and `search_name`

        data = {
            **membership.model_dump(),
            "pk": "song",
            "search_name": None,
            "random": None,
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
        mapping = {
            Kind.song: (Song, crud.read_all_songs, crud.search_song),
            Kind.composer: (Composer, crud.read_all_composers, crud.search_composer),
            Kind.collection: (
                Collection,
                crud.read_all_collections,
                crud.search_collection,
            ),
        }

        model, get_all, search_record = mapping[kind]

        if not string:
            records = sorted(get_all(), key=lambda x: x.name)
        else:
            records = search_record(string)

        # autocompletion / typing not working here due to using partial in crud
        return [model(**record.model_dump()) for record in records]


@strawberry.input
class SongInput:
    name: str
    tones: str


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
    def create_song(
        self,
        song: SongInput,
        composers: list[int] | None = None,
        collections: list[int] | None = None,
    ) -> Song:

        songdict = strawberry.asdict(song)
        song_model = models.SongCreate(**songdict)

        db_song = crud.create_song(song_model)

        # check for opus and create if needed
        if not opus.exists(song.tones):
            print("Creating new opus for", song.tones)
            opus.create(song.tones)
            print("Created new opus for", song.tones)
        else:
            print("Found existing opus for", song.tones)

        # add to collections and composers
        composers_ = composers or []
        for composer in composers_:
            crud.create_memberships(Kind.composer, composer, [db_song.id])

        # add hankkari to collections set if it is
        collections_ = set(collections or []) | (
            {7} if is_hankkari(song.tones.split("-")) else set()
        )

        for collection in collections_:
            crud.create_memberships(Kind.collection, collection, [db_song.id])

        return Song(**db_song.model_dump())

    @strawberry.mutation
    def update_song(self, id: int, name: str, tones: str) -> Song:
        song_model = models.SongUpdate(
            name=name,
            tones=tones,
        )

        db_song = crud.update_song(id, song_model)

        # ensure that membership records are updated as well
        # (this is needed due to denormalization)
        crud.update_song_memberships(id, song_model)

        return Song(**db_song.model_dump())

    @strawberry.mutation
    def delete_song(self, id: int) -> int:
        """Deletes song and all it's memberships"""
        result = crud.delete_song_cascade(id)

        return result

    @strawberry.mutation
    def create_composer(
        self, composer: ComposerInput, songs: list[int] | None = None
    ) -> Composer:
        composerdict = strawberry.asdict(composer)
        composer_model = models.ComposerCreate(**composerdict)

        db_composer = crud.create_composer(composer_model)

        # add songs
        songs_ = songs or []
        crud.create_memberships(Kind.composer, db_composer.id, songs_)

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
    def delete_composer(self, id: int) -> int:
        crud.delete_composer_cascade(id)

        return id

    @strawberry.mutation
    def create_collection(
        self, collection: CollectionInput, songs: list[int] | None = None
    ) -> Collection:
        collectiondict = strawberry.asdict(collection)
        collection_model = models.CollectionCreate(**collectiondict)

        db_collection = crud.create_collection(collection_model)

        # add songs
        songs_ = songs or []
        crud.create_memberships(Kind.collection, db_collection.id, songs_)

        return Collection(**db_collection.model_dump())

    @strawberry.mutation
    def update_collection(self, id: int, name: str) -> Collection:
        collection_model = models.CollectionUpdate(name=name)

        db_collection = crud.update_collection(id, collection_model)

        return Collection(**db_collection.model_dump())

    @strawberry.mutation
    def delete_collection(self, id: int) -> int:
        crud.delete_collection_cascade(id)
        return id

    @strawberry.mutation
    def add_membership(
        self, kind: Kind, group_id: int, song_ids: list[int]
    ) -> list[int]:
        records = crud.create_memberships(kind, group_id, song_ids)

        return [record.song_id for record in records]

    @strawberry.mutation
    def remove_membership(
        self, kind: Kind, group_id: int, song_ids: list[int]
    ) -> list[int]:
        keys = crud.delete_memberships(kind, group_id, song_ids)

        return [int(key["sk"].split(":")[1]) for key in keys]


schema = strawberry.Schema(query=Query, mutation=Mutation)
app = GraphQL(schema)
handler = Mangum(app)
