from datetime import date, datetime
from sqlalchemy.orm import Session
from . import models, schemas
from .synth import make_opus_blob


def get_songs(db: Session):
    return db.query(models.Song).all()

def get_song(db: Session, song_id: int):
    return db.query(models.Song).get(song_id)

def search_song_by_name(db: Session, q: str):
    return db.query(models.Song).filter(models.Song.name.ilike(f'{q}%')).all()

def create_song(db: Session, song: schemas.SongCreate):
    # now instead of utcnow seems to store correct time in db.
    # Should verify why. Remember to also check PUT songs
    time_now = datetime.now()
    opus_blob = make_opus_blob(song.tones.split('-'))
    db_song = models.Song(
        name=song.name,
        tones=song.tones,
        opus=opus_blob,
        created_at=time_now,
        updated_at=time_now
    )
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

def update_song(db: Session, song: schemas.SongUpdate):  
    db_song = db.query(models.Song).get(song.id)
    db_song.updated_at = datetime.now() 

    if db_song.tones != song.tones:
        db_song.opus =  make_opus_blob(song.tones.split('-'))

    for k,v in song.dict().items():
        setattr(db_song, k, v)

    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

def get_composers(db: Session):
    return db.query(models.Composer).all()

def get_composer(db: Session, composer_id: int):
    return db.query(models.Composer).get(composer_id)

def create_composer(db: Session, composer: schemas.ComposerCreate):
    db_composer = models.Composer(firstname=composer.firstname, lastname=composer.lastname)
    db.add(db_composer)
    db.commit()
    db.refresh(db_composer)
    return db_composer

def get_songs_by_composer(db: Session, composer_id: int):
    return db.query(models.Composer).get(composer_id).songs

def add_song_to_composer(db: Session, composer_id: int, song_id: int):
    db_composer = db.query(models.Composer).get(composer_id)
    db_song = db.query(models.Song).get(song_id)
    
    db_composer.songs.append(db_song)
    db.commit()
    return

def search_composers_by_lastname(db: Session, lastname: str):
    return db.query(models.Composer).filter(models.Composer.lastname.ilike(f'{lastname}%')).all()

def get_collections(db: Session):
    return db.query(models.Collection).all()

def get_collection(db: Session, collection_id: int):
    return db.query(models.Collection).get(collection_id)

def get_collection_songs(db: Session, collection_id: int):
    return db.query(models.Collection).get(collection_id).songs

def search_collections_by_name(db: Session, q: str):
    return db.query(models.Collection).filter(models.Collection.name.ilike(f'{q}%')).all()

def add_song_to_collection(db: Session, collection_id: int, song_id: int):
   db_collection = db.query(models.Collection).get(collection_id)
   db_song = db.query(models.Song).get(song_id)

   db_collection.songs.append(db_song)
   db.commit()
   return