from decimal import Decimal
from functools import partial
import random
from typing import ClassVar, Protocol, Type, TypeVar
from pydantic import BaseModel, computed_field, Field


CreateModelType = TypeVar("CreateModelType", bound=BaseModel)


class ModelType(Protocol):
    __kind__: ClassVar[str]


class KeySchema(BaseModel):
    """Everything in the DynamoDB has a partition key and a sort key"""

    pk: str
    sk: str


class Record(KeySchema):
    """Granted, a bit of a generic name, but this is mostly to differentiate
    between the records relevant to the user (Song, Composer, Collection) and
    the internal things (like opus, membership, sequence)
    """

    name: str
    random: Decimal

    @computed_field
    @property
    def id(self) -> int:
        return int(self.sk.split(":")[1])

    @computed_field
    @property
    def search_name(self) -> str:
        return self.name.lower()


class Song(Record):
    __kind__: ClassVar[str] = "song"

    tones: str


class Composer(Record):
    __kind__: ClassVar[str] = "composer"

    first_name: str | None = None
    last_name: str


class Collection(Record):
    __kind__: ClassVar[str] = "collection"


class RecordCreate(BaseModel):
    random: str = Field(default_factory=lambda: Decimal(str(random.random())))

    @computed_field
    @property
    def search_name(self) -> str:
        """This is a bit of a bad pattern, as it assumes that subclasses implement `name`
        This is due to Composer being a bit janky - couldn't yet find a way to override
        a superclass attribute with a computed field. Alternative would be to instead
        just provide the full name and parse first_name and last_name from it instead.
        """
        return self.name.lower()


class SongCreate(RecordCreate):
    name: str
    tones: str


class ComposerCreate(RecordCreate):
    first_name: str | None = None
    last_name: str

    @computed_field
    @property
    def name(self) -> str:
        return self.last_name + (f", {self.first_name}" if self.first_name else "")


class CollectionCreate(RecordCreate):
    name: str


# crud stuff - shall be moved eventually
from . import dynamodb as db


def create(data: CreateModelType, model: Type[ModelType]) -> ModelType:
    # get the id and form pk & sk
    kind = model.__kind__
    # id = db._get_next_id(kind)
    id = 123
    pk = kind
    sk = f"{kind}:{id}"

    item_in = model(**data.model_dump(), pk=pk, sk=sk)

    # db.put(...)

    return item_in


def read(id: int, model: Type[ModelType]) -> ModelType:
    pk = model.__kind__
    sk = f"{pk}:{id}"
    item = db.get_item(pk, sk)

    return model(**item)


def update():
    raise NotImplementedError


def delete(id: int, model: Type[ModelType]) -> ModelType:
    pk = model.__kind__
    sk = f"{pk}:{id}"

    print("Would now delete", pk, sk)
    # return model(**db.delete(pk, sk))


create_song = partial(create, model=Song)
create_composer = partial(create, model=Composer)
create_collection = partial(create, model=Collection)

read_song = partial(read, model=Song)
read_composer = partial(read, model=Composer)
read_collection = partial(read, model=Collection)
