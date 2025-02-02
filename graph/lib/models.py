from decimal import Decimal

import random
from typing import ClassVar, TypeVar
from pydantic import BaseModel, computed_field, Field


CreateModelType = TypeVar("CreateModelType", bound=BaseModel)
UpdateModelType = TypeVar("UpdateModelType", bound=BaseModel)


class ModelType(BaseModel):
    __kind__: ClassVar[str]


class Key(BaseModel):
    """Everything in the DynamoDB has a partition key and a sort key"""

    pk: str
    sk: str


class Membership(Key):
    """A membership record connects Songs to Groups (Collections and Composers)"""

    name: str
    tones: str

    @property
    def group_id(self) -> int:
        return int(self.pk.split(":")[1])

    @property
    def song_id(self) -> int:
        return int(self.sk.split(":")[1])


class Record(ModelType, Key):
    """Granted, a bit of a generic name, but this is mostly to differentiate
    between the records relevant to the user (Song, Composer, Collection) and
    the internal things (like opus, membership, sequence)
    """

    name: str
    random: Decimal

    # @computed_field # commented out, since should be exluded from dumps
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


# update models require that you specify all editable attributes,
# at least for now.
class SongUpdate(BaseModel):
    name: str
    tones: str


class ComposerUpdate(BaseModel):
    first_name: str | None
    last_name: str

    @computed_field
    @property
    def name(self) -> str:
        return self.last_name + (f", {self.first_name}" if self.first_name else "")


class CollectionUpdate(BaseModel):
    name: str
