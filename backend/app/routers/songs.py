from io import BytesIO
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..dependencies import get_db
from .. import schemas
from .. import crud


router = APIRouter(
    prefix='/songs',
    tags=['songs']
)

@router.get('/', response_model=List[schemas.Song])
def read_songs(db: Session = Depends(get_db)):
    return crud.get_songs(db)

@router.get('/search', response_model=List[schemas.Song])
def search_songs(q: str, db: Session = Depends(get_db)):
    db_songs = crud.search_song_by_name(db, q)
    return db_songs

@router.post('/', response_model=schemas.Song, status_code=status.HTTP_201_CREATED)
def create_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    return crud.create_song(db=db, song=song)

@router.put('/{song_id}', response_model=schemas.Song)
def update_song(song: schemas.SongUpdate, db: Session = Depends(get_db)):
    return crud.update_song(db, song)

@router.get('/{song_id}', response_model=schemas.Song)
def read_song(song_id: int, db: Session = Depends(get_db)):
    db_song = crud.get_song(db, song_id)
    if not db_song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Song not found')

    return db_song

@router.get('/{song_id}/opus')
def get_song_opus(song_id: int, db: Session = Depends(get_db)):
    file_like = crud.get_song_opus(db, song_id)
    return StreamingResponse(BytesIO(file_like), media_type='audio/ogg')
