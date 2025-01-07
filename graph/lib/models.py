from decimal import Decimal
from typing import Any
from pydantic import BaseModel, computed_field


class ComposerBase(BaseModel):
    __kind__ = "composer"

    first_name: str | None
    last_name: str

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.last_name}, {self.first_name}"

    @computed_field
    @property
    def search_name(self) -> str:
        return self.name.lower()


class ComposerCreate(ComposerBase):
    pass


class Composer(ComposerBase):
    pk: str
    sk: str

    random: Decimal


class CollectionBase(BaseModel):
    __kind__ = "collection"

    name: str

    @computed_field
    @property
    def search_name(self) -> str:
        return self.name.lower()


class CollectionCreate(CollectionBase):
    pass


class Collection(CollectionBase):
    pk: str
    sk: str

    random: Decimal


class SongBase(BaseModel):
    """Composer(s) and collections not included here, since they are currently
    a bit tricky to fetch from the db. It also isn't the most important use
    pattern, so will omit it for now. They are, however, a part of the CreateSong model.
    """

    __kind__ = "song"

    name: str
    tones: str

    @computed_field
    @property
    def search_name(self) -> str:
        return self.name.lower()


class SongCreate(SongBase):
    """The below fields are commented out, as song creation itself doesn't really require these.
    Need to think where to handle creating membership records. A GraphQL mutation could probably
    be a good place to fire off resolvers
    """

    # composer: list[ComposerCreate] = []
    # collections: list[CollectionCreate] = []


class Song(SongBase):
    pk: str
    sk: str

    random: Decimal


class Opus(BaseModel):
    pk: str
    sk: str
    opus: Any  # this should probably be handled better, see: https://docs.pydantic.dev/latest/concepts/types/#handling-third-party-types


class SearchResult(BaseModel):
    pk: str
    sk: str
    name: str | None = None
