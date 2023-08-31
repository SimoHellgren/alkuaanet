from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db
from .. import schemas
from .. import crud

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/", response_model=List[schemas.Collection])
def read_collections(db: Session = Depends(get_db), filter: str = ""):
    return crud.get_collections(db, filter)


@router.get("/{collection_id}", response_model=schemas.Collection)
def read_collection(collection_id: int, db: Session = Depends(get_db)):
    return crud.get_collection(db, collection_id)


@router.get("/{collection_id}/songs", response_model=List[schemas.Song])
def read_collection_songs(collection_id: int, db: Session = Depends(get_db)):
    return crud.get_collection_songs(db, collection_id)


@router.put("/{collection_id}/songs/{song_id}")
def add_song_to_collection(
    collection_id: int, song_id: int, db: Session = Depends(get_db)
):
    return crud.add_song_to_collection(db, collection_id, song_id)
