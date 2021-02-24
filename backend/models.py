from sqlalchemy import Table, Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from .database import Base

collection_songs = Table(
    'collection_song',
    Base.metadata,
    Column('collection_id', Integer, ForeignKey('collection.id')),
    Column('song_id', Integer, ForeignKey('song.id'))
)

composer_songs = Table(
    'composer_song',
    Base.metadata,
    Column('composer_id', Integer, ForeignKey('composer.id')),
    Column('song_id', Integer, ForeignKey('song.id'))
)

class Collection(Base):
    __tablename__ = 'collection'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    songs = relationship('Song', secondary=collection_songs, back_populates='collections')

class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tones = Column(String)
    opus = Column(LargeBinary)

    composers = relationship('Composer', secondary=composer_songs, back_populates='songs')

    collections = relationship('Collection', secondary=collection_songs, back_populates='songs')

class Composer(Base):
    __tablename__ = 'composer'

    id = Column(Integer, primary_key=True)
    lastname = Column(String)
    firstname = Column(String)

    songs = relationship('Song', secondary=composer_songs, back_populates='composers')
