import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "hotel.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            available INTEGER NOT NULL DEFAULT 1,
            notes TEXT
        )
        """
    )
    conn.commit()
    conn.close()
