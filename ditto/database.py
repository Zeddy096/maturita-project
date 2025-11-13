import sqlite3
import os

DB_PATH = os.path.join("data", "recepty.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS recepty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazev TEXT NOT NULL,
            cas TEXT,
            suroviny TEXT,
            postup TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_recept(nazev, cas, suroviny, postup):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO recepty (nazev, cas, suroviny, postup) VALUES (?, ?, ?, ?)",
        (nazev, cas, suroviny, postup),
    )
    conn.commit()
    conn.close()

def get_recepty():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, nazev, cas FROM recepty ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

def get_recept(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM recepty WHERE id = ?", (id,))
    data = c.fetchone()
    conn.close()
    return data