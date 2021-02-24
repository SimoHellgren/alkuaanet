from fastapi import FastAPI
from . import models
from .database import engine
from .routers import songs, composers, collections

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(songs.router)
app.include_router(composers.router)
app.include_router(collections.router)

@app.get('/')
def root():
    return 'Hello there!'
