import sqlite3
from datetime import datetime
import json
import random
import asyncio
from datetime import datetime, timedelta

class DatabaseTool:
    def __init__(self, fileName):
        self.conn = sqlite3.connect(fileName, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def __exit__(self, exc_type, exc, tb):
        # commit if no error, otherwise rollback
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.close()

    def close(self):
        # ✅ free locks on Windows
        try:
            self.cursor.close()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass

    def createTableIfNotExist(self):
        self.cursor.executescript(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            );

            CREATE TABLE IF NOT EXISTS plays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCE,
                song_id INTEGER,
                played_at TEXT 
            );

            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                artist TEXT
            );

            '''
        )

    def addUser(self, name):
        query = '''INSERT INTO users(name) VALUES (?)'''
        self.cursor.execute(query, (name,))
        self.conn.commit()

    def addSong(self, title, artist):
        query = '''INSERT INTO songs(title, artist) VALUES (?, ?)'''
        self.cursor.execute(query, (title, artist))
        self.conn.commit()
       


    def addListen(self, userId, songId):
        currentTime = datetime.now()
        query = '''INSERT INTO plays(user_id, song_id, played_at) VALUES (?, ?, ?)'''
        self.cursor.execute(query, (userId, songId, currentTime))   
        self.conn.commit()
        

    def getTable(self, table):
        try:
            query = f'''SELECT * FROM {table}'''
            self.conn.row_factory = sqlite3.Row
            self.cursor.execute(query)
            

            rows = self.cursor.fetchall()
            print(type(rows[0]))

            columns = [desc[0] for desc in self.cursor.description]

            return [dict(zip(columns, row)) for row in rows]
        

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")


    def getSong(self, songId: int | None = None, artist: str | None = None):
            print("Database Call")
            query = "SELECT title, artist FROM songs WHERE 1=1"
            params = []

            # And it in filter
            if songId is not None:
                query += " AND id = ?"
                params.append(songId)
            if artist is not None:
                query += " AND artist = ?"
                params.append(artist)


            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()

            columns = [desc[0] for desc in self.cursor.description]

            return [dict(zip(columns, row)) for row in rows]
            
    
            


