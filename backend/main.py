from io import BytesIO
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

find = lambda f, it, default=None: next(filter(f, it), default)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

@app.get('/')
def root():
    return 'hey.'

@app.get('/songs', response_model=List[schemas.Song])
def read_songs(db: Session = Depends(get_db)):
    return crud.get_songs(db)


@app.post('/songs', response_model=schemas.Song)
def create_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    return crud.create_song(db=db, song=song)
    

@app.put('/songs/{song_id}', response_model=schemas.Song)
def update_song(song: schemas.Song, db: Session = Depends(get_db)):
    return crud.update_song(db, song)

@app.get('/songs/{song_id}', response_model=schemas.Song)
def read_song(song_id: int, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id)
    if not db_song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Song not found')

    return db_song

@app.get('/songs/{song_id}/opus')
def get_song_opus(song_id: int, db: Session = Depends(get_db)):
    file_like = crud.get_song_opus(db, song_id)
    return StreamingResponse(BytesIO(file_like), media_type='audio/ogg')

@app.get('/songs/search/{q}', response_model=List[schemas.Song])
def search_songs(q: str, db: Session = Depends(get_db)):
    db_songs = crud.search_song_by_name(db, q)
    return db_songs

@app.get('/composers', response_model=List[schemas.Composer])
def read_composers(db: Session = Depends(get_db)):
    return crud.get_composers(db)

@app.post('/composers', response_model=schemas.Composer)
def create_composer(composer: schemas.ComposerCreate, db: Session = Depends(get_db)):
    return crud.create_composer(db, composer)

@app.get('/composers/{composer_id}', response_model=schemas.Composer)
def read_composer(composer_id: int, db: Session = Depends(get_db)):
    return crud.get_composer(db, composer_id)

@app.get('/composers/{composer_id}/songs', response_model=List[schemas.Song])
def read_composer_songs(composer_id: int, db: Session = Depends(get_db)):
    return crud.get_songs_by_composer(db, composer_id)

@app.put('/composers/{composer_id}/songs/{song_id}')
def add_song_to_composer(composer_id: int, song_id: int, db: Session = Depends(get_db)):
    return crud.add_song_to_composer(db, composer_id, song_id)

@app.get('/composers/search/{lastname}', response_model=List[schemas.Composer])
def search_composers(lastname: str, db: Session = Depends(get_db)):
    return crud.search_composers_by_lastname(db, lastname)

@app.get('/collections', response_model=List[schemas.Collection])
def read_collection(db: Session = Depends(get_db)):
    return crud.get_collections(db)

@app.get('/collections/{collection_id}', response_model=schemas.Collection)
def read_collection(collection_id: int, db: Session = Depends(get_db)):
    return crud.get_collection(db, collection_id)

@app.get('/collections/{collection_id}/songs', response_model=List[schemas.Song])
def read_collection_songs(collection_id: int, db: Session = Depends(get_db)):
    return crud.get_collection_songs(db, collection_id)

@app.put('/collections/{collection_id}/songs/{song_id}')
def add_song_to_collection(collection_id: int, song_id: int, db: Session = Depends(get_db)):
    return crud.add_song_to_collection(db, collection_id, song_id)

@app.get('/collections/search/{q}', response_model=List[schemas.Collection])
def search_songs_by_collection_name(q: str, db: Session = Depends(get_db)):
    return crud.search_collections_by_name(db, q)
