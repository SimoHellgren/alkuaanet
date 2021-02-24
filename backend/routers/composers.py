from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db
from .. import schemas
from .. import crud

router = APIRouter()

@router.get('/composers', response_model=List[schemas.Composer])
def read_composers(db: Session = Depends(get_db)):
    return crud.get_composers(db)

@router.post('/composers', response_model=schemas.Composer)
def create_composer(composer: schemas.ComposerCreate, db: Session = Depends(get_db)):
    return crud.create_composer(db, composer)

@router.get('/composers/{composer_id}', response_model=schemas.Composer)
def read_composer(composer_id: int, db: Session = Depends(get_db)):
    return crud.get_composer(db, composer_id)

@router.get('/composers/{composer_id}/songs', response_model=List[schemas.Song])
def read_composer_songs(composer_id: int, db: Session = Depends(get_db)):
    return crud.get_songs_by_composer(db, composer_id)

@router.put('/composers/{composer_id}/songs/{song_id}')
def add_song_to_composer(composer_id: int, song_id: int, db: Session = Depends(get_db)):
    return crud.add_song_to_composer(db, composer_id, song_id)

@router.get('/composers/search/{lastname}', response_model=List[schemas.Composer])
def search_composers(lastname: str, db: Session = Depends(get_db)):
    return crud.search_composers_by_lastname(db, lastname)