import sqlite3
from datetime import datetime
import json
import random
from datetime import datetime, timedelta

class DatabaseTool:
    def __init__(self, fileName):
        self.conn = sqlite3.connect(fileName)
        self.cursor = self.conn.cursor()

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


    def seed_plays(self, num_plays=1000):
        user_ids = list(range(1, 6))      # users 1–5
        song_ids = list(range(1, 16))     # songs 1–15

        base_time = datetime.now() - timedelta(days=30)

        for _ in range(num_plays):
            user_id = random.choice(user_ids)
            song_id = random.choice(song_ids)

            # random time in last 30 days
            played_at = base_time + timedelta(
                seconds=random.randint(0, 30 * 24 * 3600)
            )

            query = """
                INSERT INTO plays(user_id, song_id, played_at)
                VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (user_id, song_id, played_at.isoformat()))

        self.conn.commit()

