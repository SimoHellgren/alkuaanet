from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from ..dependencies import get_db
from .. import schemas
from .. import crud

router = APIRouter(prefix="/composers", tags=["composers"])


@router.get("/", response_model=List[schemas.Composer])
def read_composers(db: Session = Depends(get_db)):
    return crud.get_composers(db)


@router.get("/search", response_model=List[schemas.Composer])
def search_composers(lastname: str, db: Session = Depends(get_db)):
    return crud.search_composers_by_lastname(db, lastname)


@router.post("/", response_model=schemas.Composer, status_code=status.HTTP_201_CREATED)
def create_composer(composer: schemas.ComposerCreate, db: Session = Depends(get_db)):
    return crud.create_composer(db, composer)


@router.get("/{composer_id}", response_model=schemas.Composer)
def read_composer(composer_id: int, db: Session = Depends(get_db)):
    return crud.get_composer(db, composer_id)


@router.get("/{composer_id}/songs", response_model=List[schemas.Song])
def read_composer_songs(composer_id: int, db: Session = Depends(get_db)):
    return crud.get_songs_by_composer(db, composer_id)


@router.put("/{composer_id}/songs/{song_id}")
def add_song_to_composer(composer_id: int, song_id: int, db: Session = Depends(get_db)):
    return crud.add_song_to_composer(db, composer_id, song_id)
