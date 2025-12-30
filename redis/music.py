import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "music.db"

NUM_USERS = 1000
NUM_SONGS = 5000
NUM_PLAYS = 200_000

random.seed(42)

VIET_FIRST = [
    "An", "Bình", "Châu", "Dũng", "Duy", "Giang", "Hà", "Hải", "Hạnh", "Hiếu",
    "Hòa", "Hùng", "Khánh", "Khoa", "Lan", "Linh", "Long", "Minh", "Nam", "Nga",
    "Ngọc", "Nhi", "Phong", "Phúc", "Quân", "Sơn", "Tâm", "Thảo", "Trang", "Tú", "Vy"
]
VIET_LAST = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"
]

ARTISTS = [
    "Sơn Tùng M-TP", "Mỹ Tâm", "Đen", "Bích Phương", "Vũ.", "Hoàng Thùy Linh",
    "Hà Anh Tuấn", "Noo Phước Thịnh", "Hương Tràm", "MIN", "Chi Pu", "ERIK",
    "Jack", "AMEE", "Trúc Nhân", "Phan Mạnh Quỳnh", "JustaTee", "Tóc Tiên",
    "Dalab", "Ngọt"
]

TITLE_WORDS = [
    "Mùa", "Hạ", "Đông", "Gió", "Mưa", "Nắng", "Yêu", "Thương", "Nhớ", "Quên",
    "Đợi", "Về", "Xa", "Gần", "Mộng", "Buồn", "Vui", "Ngày", "Đêm", "Phố",
    "Biển", "Trời", "Tim", "Em", "Anh", "Ta", "Một", "Lần", "Cuối", "Đầu"
]


def random_name():
    return f"{random.choice(VIET_LAST)} {random.choice(VIET_FIRST)}"


def random_title():
    # create 2-5 word titles
    k = random.randint(2, 5)
    return " ".join(random.choice(TITLE_WORDS) for _ in range(k))


def make_schema(cur: sqlite3.Cursor):
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        artist TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS plays (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
        played_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (song_id) REFERENCES songs(id)
    );

    -- indexes for faster queries
    CREATE INDEX IF NOT EXISTS idx_plays_song_id ON plays(song_id);
    CREATE INDEX IF NOT EXISTS idx_plays_user_id ON plays(user_id);
    CREATE INDEX IF NOT EXISTS idx_plays_played_at ON plays(played_at);
    """)


def seed_users(cur: sqlite3.Cursor, n: int):
    users = [(random_name(),) for _ in range(n)]
    cur.executemany("INSERT INTO users(name) VALUES (?)", users)


def seed_songs(cur: sqlite3.Cursor, n: int):
    songs = []
    for _ in range(n):
        title = random_title()
        artist = random.choice(ARTISTS)
        songs.append((title, artist))
    cur.executemany("INSERT INTO songs(title, artist) VALUES (?, ?)", songs)


def seed_plays(cur: sqlite3.Cursor, num_users: int, num_songs: int, n: int):
    """
    Generate realistic-ish listening:
    - 20% of songs get 80% of plays (Zipf-ish / popularity skew)
    """
    now = datetime.now()
    start = now - timedelta(days=60)  # last 60 days

    popular_cutoff = max(1, int(num_songs * 0.2))
    popular_songs = list(range(1, popular_cutoff + 1))
    other_songs = list(range(popular_cutoff + 1, num_songs + 1))

    plays_batch = []
    BATCH_SIZE = 10_000

    for i in range(1, n + 1):
        user_id = random.randint(1, num_users)

        if random.random() < 0.8:
            # 80% chance pick from popular 20% songs
            song_id = random.choice(popular_songs)
        else:
            song_id = random.choice(other_songs)

        # random timestamp in last 60 days
        delta = random.random()
        played_at = (start + (now - start) * delta).strftime("%Y-%m-%dT%H:%M:%S")

        plays_batch.append((user_id, song_id, played_at))

        if len(plays_batch) >= BATCH_SIZE:
            cur.executemany(
                "INSERT INTO plays(user_id, song_id, played_at) VALUES (?, ?, ?)",
                plays_batch,
            )
            plays_batch.clear()

    if plays_batch:
        cur.executemany(
            "INSERT INTO plays(user_id, song_id, played_at) VALUES (?, ?, ?)",
            plays_batch,
        )


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL;")  # faster writes
    conn.execute("PRAGMA synchronous = NORMAL;")
    cur = conn.cursor()

    make_schema(cur)

    # Clear existing data (optional). Comment out if you want to keep old data.
    cur.executescript("""
    DELETE FROM plays;
    DELETE FROM songs;
    DELETE FROM users;
    """)

    print("Seeding users...")
    seed_users(cur, NUM_USERS)
    print("Seeding songs...")
    seed_songs(cur, NUM_SONGS)
    print("Seeding plays (this is the big one)...")
    seed_plays(cur, NUM_USERS, NUM_SONGS, NUM_PLAYS)

    conn.commit()

    # quick sanity checks
    users = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    songs = cur.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
    plays = cur.execute("SELECT COUNT(*) FROM plays").fetchone()[0]
    print(f"Done. users={users}, songs={songs}, plays={plays}")
    print(f"Database saved to: {DB_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
