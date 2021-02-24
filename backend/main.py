from fastapi import FastAPI, Depends
from typing import List
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from .routers import songs, composers

models.Base.metadata.create_all(bind=engine)

find = lambda f, it, default=None: next(filter(f, it), default)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

app.include_router(songs.router)
app.include_router(composers.router)

@app.get('/')
def root():
    return 'hey.'

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
