from functools import partial
from typing import Type

from .models import CreateModelType, UpdateModelType, ModelType
from .models import Song, SongUpdate, Composer, Collection, Membership, Key
from . import dynamodb as db


def search(string: str, model: Type[ModelType]) -> ModelType:
    items = db.search(model.__kind__, string)

    return [model(**item) for item in items]


def create(data: CreateModelType, model: Type[ModelType]) -> ModelType:
    # get the id and form pk & sk
    kind = model.__kind__
    id = db._get_next_id(kind)
    pk = kind
    sk = f"{kind}:{id}"

    item_in = model(**data.model_dump(), pk=pk, sk=sk)

    item = db.put(item_in.model_dump())

    # it is a bit funky that we don't return the object from the db, but eh
    return item_in


def read(id: int, model: Type[ModelType]) -> ModelType | None:
    pk = model.__kind__
    sk = f"{pk}:{id}"
    item = db.get_item(pk, sk)

    if not item:
        return None

    return model(**item)


def read_many(ids: list[int], model: Type[ModelType]) -> list[ModelType]:
    pk = model.__kind__
    sks = [f"{pk}:{id}" for id in ids]
    keys = [{"pk": pk, "sk": sk} for sk in sks]

    items = db.batch_get(keys)

    return [model(**item) for item in items]


def read_all(model: Type[ModelType]) -> ModelType:
    items = db.get_partition(model.__kind__)

    return [model(**item) for item in items]


def update(id: int, data: UpdateModelType, model: Type[ModelType]) -> ModelType:
    kind = model.__kind__
    db_record = db.get_item(kind, f"{kind}:{id}")

    updated = model(
        **{
            **db_record,
            **data.model_dump(),
        }
    )

    item = db.put(updated.model_dump())

    return updated


def delete(id: int, model: Type[ModelType]) -> ModelType:
    pk = model.__kind__
    sk = f"{pk}:{id}"

    return model(**db.delete(pk, sk))


def get_group_songs(id: int, kind: str) -> list[Membership]:
    items = db.get_partition(f"{kind}:{id}")

    return [Membership(**item) for item in items]


def delete_group_cascade(id: int, kind: str) -> int:
    # using the lower-level ProjectionExpression here isn't all that nice
    keys = db.get_partition(f"{kind}:{id}", ProjectionExpression="pk, sk")

    db.batch_delete([*keys, {"pk": kind, "sk": f"{kind}:{id}"}])

    return id


# these do not properly bind to the appropriate create and update types, but
# this shall be considered later
create_song = partial(create, model=Song)
read_song = partial(read, model=Song)
read_many_songs = partial(read_many, model=Song)
read_all_songs = partial(read_all, model=Song)
update_song = partial(update, model=Song)
delete_song = partial(delete, model=Song)
search_song = partial(search, model=Song)


def get_random_song() -> Song:
    return Song(**db.random("song"))


def get_song_memberships(id: int) -> list[Key]:
    results = db.reverse_index(sk=f"song:{id}")
    records = [r for r in results if r["pk"] != "song"]

    if not records:
        return []

    keys = [Key(**record) for record in records]
    return keys


def update_song_memberships(id: int, data: SongUpdate) -> int:
    """Find the membership records for the song, and update them"""
    results = db.reverse_index(sk=f"song:{id}")
    records = [r for r in results if r["pk"] != "song"]
    memberships = [
        Membership(
            pk=record["pk"],
            sk=record["sk"],
            name=data.name,
            tones=data.tones,
        )
        for record in records
    ]

    db.batch_write([m.model_dump() for m in memberships])

    return id


def delete_song_cascade(id: int) -> int:
    keys = db.reverse_index(sk=f"song:{id}")

    db.batch_delete(keys)

    return id


create_composer = partial(create, model=Composer)
read_composer = partial(read, model=Composer)
read_many_comopsers = partial(read_many, model=Composer)
read_all_composers = partial(read_all, model=Composer)
update_composer = partial(update, model=Composer)
delete_composer = partial(delete, model=Composer)
get_composer_songs = partial(get_group_songs, kind="composer")
delete_composer_cascade = partial(delete_group_cascade, kind="composer")
search_composer = partial(search, model=Composer)

create_collection = partial(create, model=Collection)
read_collection = partial(read, model=Collection)
read_many_collections = partial(read_many, model=Collection)
read_all_collections = partial(read_all, model=Collection)
update_collection = partial(update, model=Collection)
delete_collection = partial(delete, model=Collection)
get_collection_songs = partial(get_group_songs, kind="collection")
delete_collection_cascade = partial(delete_group_cascade, kind="collection")
search_collection = partial(search, model=Collection)


def create_memberships(
    kind: str, group_id: int, song_ids: list[int]
) -> list[Membership]:
    songs = db.batch_get([{"pk": "song", "sk": f"song:{id}"} for id in song_ids])

    items = [
        Membership(
            pk=f"{kind}:{group_id}",
            sk=song["sk"],
            name=song["name"],
            tones=song["tones"],
        )
        for song in songs
    ]

    db.batch_write([item.model_dump() for item in items])

    return items


def delete_memberships(kind: str, group_id: int, song_ids: list[int]) -> list[dict]:
    deleted = db.batch_delete(
        [{"pk": f"{kind}:{group_id}", "sk": f"song:{id}"} for id in song_ids]
    )

    return deleted
