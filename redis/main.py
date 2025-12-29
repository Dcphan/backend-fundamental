# Python Libraries
from fastapi import FastAPI
import uvicorn
import asyncio
from db import DatabaseTool
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str

class Song(BaseModel):
    title: str
    artist: str

class Play(BaseModel):
    userId: int
    songId: int
    
database = DatabaseTool("music_list.db")

@app.post("/users")
async def addUser(item: User):
    database.addUser(item.name)
    return item

@app.post("/songs")
async def addUser(item: Song):
    database.addSong(item.title, item.artist)
    return item

@app.post("/plays")
async def addUser(item: Play):
    database.addListen(item.userId, item.songId)
    return item

@app.get("/users")
async def getUser():
    data = database.getTable("users")
    return data

@app.get("/songs")
async def getUser():
    data = database.getTable("songs")
    return data

@app.get("/plays")
async def getUser():
    data = database.getTable("plays")
    return data



