import sqlite3

conn = sqlite3.conn("music_list.db")

cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users
    '''
)