import sqlite3

DB_NAME = "app.db"

def init_settings_db():
    with sqlite3.connect(DB_NAME) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        con.commit()

def set_setting(key: str, value: str):
    with sqlite3.connect(DB_NAME) as con:
        con.execute(
            "INSERT INTO app_settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        con.commit()

def get_setting(key: str, default: str = "") -> str:
    with sqlite3.connect(DB_NAME) as con:
        cur = con.execute("SELECT value FROM app_settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default
