from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ComposerBase(BaseModel):
    lastname: str
    firstname: Optional[str] = None


class ComposerCreate(ComposerBase):
    pass


class Composer(ComposerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SongBase(BaseModel):
    name: str


class SongCreate(SongBase):
    tones: str


class SongUpdate(SongBase):
    id: int
    name: str
    tones: str


class Song(SongBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tones: Optional[str]
    created_at: datetime
    updated_at: datetime


class CollectionBase(BaseModel):
    name: str


class CollectionCreate(CollectionBase):
    pass


class Collection(CollectionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
