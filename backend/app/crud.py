from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from . import models, schemas
from .synth import make_opus_blob
from .odata.filter_parser import parse_odata_filter


def get_songs(db: Session, query=None):
    expr = parse_odata_filter(query)
    return db.query(models.Song).filter(text(expr)).all()


def get_song(db: Session, song_id: int):
    return db.get(models.Song, song_id)


def create_song(db: Session, song: schemas.SongCreate):
    # now instead of utcnow seems to store correct time in db.
    # Should verify why. Remember to also check PUT songs
    time_now = datetime.now()
    opus_blob = make_opus_blob(song.tones.split("-"))
    db_song = models.Song(
        name=song.name,
        tones=song.tones,
        opus=opus_blob,
        created_at=time_now,
        updated_at=time_now,
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def update_song(db: Session, song: schemas.SongUpdate):
    db_song = db.get(models.Song, song.id)
    db_song.updated_at = datetime.now()

    if db_song.tones != song.tones:
        db_song.opus = make_opus_blob(song.tones.split("-"))

    for k, v in song.model_dump().items():
        setattr(db_song, k, v)

    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song


def get_composers(db: Session, query=None):
    expr = parse_odata_filter(query)
    return db.query(models.Composer).filter(text(expr)).all()


def get_composer(db: Session, composer_id: int):
    return db.get(models.Composer, composer_id)


def create_composer(db: Session, composer: schemas.ComposerCreate):
    db_composer = models.Composer(
        firstname=composer.firstname, lastname=composer.lastname
    )
    db.add(db_composer)
    db.commit()
    db.refresh(db_composer)
    return db_composer


def get_songs_by_composer(db: Session, composer_id: int):
    return db.get(models.Composer, composer_id).songs


def add_song_to_composer(db: Session, composer_id: int, song_id: int):
    db_composer = db.get(models.Composer, composer_id)
    db_song = db.get(models.Song, song_id)

    db_composer.songs.append(db_song)
    db.commit()
    return


def get_collections(db: Session, query=None):
    expr = parse_odata_filter(query)
    return db.query(models.Collection).filter(text(expr)).all()


def get_collection(db: Session, collection_id: int):
    return db.get(models.Collection, collection_id)


def create_collection(db: Session, collection: schemas.CollectionCreate):
    db_collection = models.Collection(name=collection.name)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)

    return db_collection


def get_collection_songs(db: Session, collection_id: int):
    return db.get(models.Collection, collection_id).songs


def search_collections_by_name(db: Session, q: str):
    return (
        db.query(models.Collection).filter(models.Collection.name.ilike(f"{q}%")).all()
    )


def add_song_to_collection(db: Session, collection_id: int, song_id: int):
    db_collection = db.get(models.Collection, collection_id)
    db_song = db.get(models.Song, song_id)

    db_collection.songs.append(db_song)
    db.commit()
    return
