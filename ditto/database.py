# database.py -- jednoduchý wrapper pro sqlite3
import sqlite3
import os

SCHEMA = """
CREATE TABLE IF NOT EXISTS recepty (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazev TEXT NOT NULL,
    cas TEXT,
    suroviny TEXT,
    postup TEXT
);
"""

SAMPLE = [
    ("Smažený sýr", "15 min", "sýr, strouhanka, vejce, olej", "obalit a osmažit"),
    ("Rychlá polévka", "20 min", "brambory, mrkev, voda, sůl", "uvařit vše do měkka"),
]

class Database:
    def __init__(self, path="data/recepty.db"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.executescript(SCHEMA)
        self.conn.commit()
        # pokud je tabulka prázdná, naplnit vzorovými daty
        cur.execute("SELECT COUNT(*) as c FROM recepty")
        if cur.fetchone()["c"] == 0:
            for nazev, cas, suroviny, postup in SAMPLE:
                self.add_recept(nazev, cas, suroviny, postup)

    def get_all_recepty(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM recepty ORDER BY id DESC")
        return [dict(row) for row in cur.fetchall()]

    def get_recept(self, rid):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM recepty WHERE id = ?", (rid,))
        row = cur.fetchone()
        return dict(row) if row else None

    def search_recepty(self, query, filter_by="nazev"):
        q = f"%{query}%"
        cur = self.conn.cursor()
        if filter_by == "cas":
            cur.execute("SELECT * FROM recepty WHERE cas LIKE ? ORDER BY id DESC", (q,))
        elif filter_by == "suroviny":
            cur.execute("SELECT * FROM recepty WHERE suroviny LIKE ? ORDER BY id DESC", (q,))
        else:
            cur.execute("SELECT * FROM recepty WHERE nazev LIKE ? ORDER BY id DESC", (q,))
        return [dict(row) for row in cur.fetchall()]

    def add_recept(self, nazev, cas, suroviny, postup):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO recepty (nazev, cas, suroviny, postup) VALUES (?, ?, ?, ?)",
            (nazev, cas or "", suroviny or "", postup or "")
        )
        self.conn.commit()
        return cur.lastrowid

    def update_recept(self, rid, nazev, cas, suroviny, postup):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE recepty SET nazev=?, cas=?, suroviny=?, postup=? WHERE id=?",
            (nazev, cas, suroviny, postup, rid)
        )
        self.conn.commit()
        return cur.rowcount

    def delete_recept(self, rid):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM recepty WHERE id=?", (rid,))
        self.conn.commit()
        return cur.rowcount
