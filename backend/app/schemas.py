from pydantic import BaseModel  
from typing import Optional
from datetime import datetime


class ComposerBase(BaseModel):
    lastname: str
    firstname: str = None

class ComposerCreate(ComposerBase):
    pass

class Composer(ComposerBase):
    id: int

    class Config:
        orm_mode = True

class SongBase(BaseModel):
    name: str

class SongCreate(SongBase):
    tones: str

class SongUpdate(SongBase):
    id: int
    name: str
    tones: str

class Song(SongBase):
    id: int
    tones: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CollectionBase(BaseModel):
    name: str

class Collection(CollectionBase):
    id: int

    class Config:
        orm_mode = True