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

def update_recept(id, nazev, cas, suroviny, postup):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE recepty SET nazev=?, cas=?, suroviny=?, postup=? WHERE id=?",
        (nazev, cas, suroviny, postup, id),
    )
    conn.commit()
    conn.close()

def delete_recept(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM recepty WHERE id=?", (id,))
    conn.commit()
    conn.close()

def search_recepty(text, mode="nazev"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    pattern = f"%{text}%"
    if mode == "cas":
        c.execute(
            "SELECT id, nazev, cas FROM recepty WHERE cas LIKE ? ORDER BY id DESC",
            (pattern,)
        )    
    elif mode == "suroviny":
        c.execute(
            "SELECT id, nazev, cas FROM recepty WHERE suroviny LIKE ? ORDER BY id DESC",
            (pattern,)
        )    
    else:
        c.execute(
            "SELECT id, nazev, cas FROM recepty WHERE cas LIKE ? ORDER BY id DESC",
            (pattern,)
        )   
    data = c.fetchall()
    conn.close()
    return data         