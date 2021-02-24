from fastapi import FastAPI, Depends
from typing import List
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from .routers import songs, composers, collections

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
app.include_router(collections.router)

@app.get('/')
def root():
    return 'hey.'
