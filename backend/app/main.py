from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import songs, composers, collections
from .config import allowed_origins


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=['*']
)

app.include_router(songs.router)
app.include_router(composers.router)
app.include_router(collections.router)

@app.get('/')
def root():
    return 'Hello there!'
