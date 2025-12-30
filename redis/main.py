# Python Libraries
from fastapi import FastAPI, Depends
import uvicorn
import asyncio
from learn_redis import CachingLayer
from db import DatabaseTool
from pydantic import BaseModel
import time
import redis

app = FastAPI()

class User(BaseModel):
    name: str

class Song(BaseModel):
    title: str
    artist: str

class Play(BaseModel):
    userId: int
    songId: int

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # Log or print the process time (e.g., to a log file or console)
    print(f"Endpoint: {request.url.path} | Process Time: {process_time:.4f} seconds")
    response.headers["X-Process-Time"] = str(process_time)
    return response
    
def get_db():
    database = DatabaseTool("music.db")
    try:
        yield database
    finally:
        database.close()

def get_cache():
    cache = CachingLayer()
    try:
        yield cache
    finally:
        cache.close()

@app.post("/users")
async def addUser(item: User, database: DatabaseTool = Depends(get_db)):
    database.addUser(item.name)
    return item

@app.post("/songs")
async def addUser(item: Song, database: DatabaseTool = Depends(get_db)):
    database.addSong(item.title, item.artist)
    return item

@app.post("/plays")
async def addUser(item: Play, database: DatabaseTool = Depends(get_db)):
    database.addListen(item.userId, item.songId)
    return item

@app.get("/users")
async def getUser(database: DatabaseTool = Depends(get_db)):
    data = database.getTable("users")
    return data

@app.get("/plays")
async def getUser(database: DatabaseTool = Depends(get_db)):
    data = database.getTable("plays")
    return data


@app.get("/songs/noncache")
async def getSongWithoutCache(
    id: int | None = None,
    artist: str | None = None,
    database: DatabaseTool = Depends(get_db)
):
    print("FastAPI call")
    data = database.getSong(songId=id, artist= artist)
    return data

@app.get("/songs/cache")
async def getSongWithoutCache(
    id: int | None = None,
    artist: str | None = None,
    database: DatabaseTool = Depends(get_db),
    cache: CachingLayer = Depends(get_cache)
):
    print("FastAPI call")
    data = cache.getSongByArtist(artist)
    if data is not None:
        print("Cache Hit")
        return data
    print("Cache Miss")
    data = database.getSong(songId=id, artist= artist)
    cache.setSongByArtist(artist, data, 300)
    return data




