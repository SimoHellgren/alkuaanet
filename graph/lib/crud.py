from functools import partial
from typing import Type

from .models import CreateModelType, UpdateModelType, ModelType
from .models import Song, Composer, Collection
from . import dynamodb as db


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


def read(id: int, model: Type[ModelType]) -> ModelType:
    pk = model.__kind__
    sk = f"{pk}:{id}"
    item = db.get_item(pk, sk)

    return model(**item)


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


# these do not properly bind to the appropriate create and update types, but
# this shall be considered later
create_song = partial(create, model=Song)
read_song = partial(read, model=Song)
read_all_songs = partial(read_all, model=Song)
update_song = partial(update, model=Song)
delete_song = partial(delete, model=Song)

create_composer = partial(create, model=Composer)
read_composer = partial(read, model=Composer)
read_all_composers = partial(read_all, model=Composer)
update_composer = partial(update, model=Composer)
delete_composer = partial(delete, model=Composer)

create_collection = partial(create, model=Collection)
read_collection = partial(read, model=Collection)
read_all_collections = partial(read_all, model=Collection)
update_collection = partial(update, model=Collection)
delete_collection = partial(delete, model=Collection)
