from fastapi import FastAPI
from .routers import songs, composers, collections


app = FastAPI()

app.include_router(songs.router)
app.include_router(composers.router)
app.include_router(collections.router)

@app.get('/')
def root():
    return 'Hello there!'
