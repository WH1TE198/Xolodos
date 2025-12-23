import sqlite3
from contextlib import closing

DB_PATH = "app.db"

def _conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT,         -- 'm' / 'f' / NULL
                birth TEXT,          -- строкой 'ДД.ММ.ГГГГ'
                height_cm REAL,
                weight_kg REAL
            );
        """)
        conn.commit()

def insert_profile(data: dict) -> int:
    """Вставляет новую строку, возвращает id."""
    with _conn() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            INSERT INTO user_profile (name, gender, birth, height_cm, weight_kg)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get("name"),
            data.get("gender"),
            data.get("birth"),
            data.get("height_cm"),
            data.get("weight_kg"),
        ))
        conn.commit()
        return cur.lastrowid

def list_profiles(limit: int = 50):
    with _conn() as conn, closing(conn.cursor()) as cur:
        rows = cur.execute("""
            SELECT id, name, gender, birth, height_cm, weight_kg
            FROM user_profile
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [
        {
            "id": r[0], "name": r[1], "gender": r[2], "birth": r[3],
            "height_cm": r[4], "weight_kg": r[5]
        } for r in rows
    ]

def last_profile_or_empty():
    """Нужна только чтобы подставить значения по умолчанию в форму."""
    items = list_profiles(limit=1)
    if not items:
        return {"name": "", "gender": None, "birth": "", "height_cm": None, "weight_kg": None}
    return items[0]
