# products_db.py
import sqlite3
from contextlib import closing

DB_PATH = "products.db"

def _conn():
    return sqlite3.connect(DB_PATH)

def init_products_db():
    with _conn() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                exp_date TEXT  -- строкой: 'ДД.ММ.ГГГГ'
            );
        """)
        conn.commit()

def insert_product(data: dict) -> int:
    with _conn() as conn, closing(conn.cursor()) as cur:
        cur.execute("""
            INSERT INTO products (name, category, exp_date)
            VALUES (?, ?, ?)
        """, (data.get("name"), data.get("category"), data.get("exp_date")))
        conn.commit()
        return cur.lastrowid

def list_products(limit: int = 100):
    with _conn() as conn, closing(conn.cursor()) as cur:
        rows = cur.execute("""
            SELECT id, name, category, exp_date
            FROM products
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [{"id": r[0], "name": r[1], "category": r[2], "exp_date": r[3]} for r in rows]

def delete_product(product_id: int) -> None:
    """Удаляет продукт по id."""
    with _conn() as conn, closing(conn.cursor()) as cur:
        cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
