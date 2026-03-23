import sqlite3
import os
import re
import shutil

DB_PATH = os.path.join("data", "recepty.db")
IMG_DIR = os.path.join("data", "images")

def _connect():
    return sqlite3.connect(DB_PATH)

def _has_column(conn, table, col):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    return col in cols

def init_db():
    os.makedirs("data", exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    conn = _connect()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS recepty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nazev TEXT NOT NULL,
            cas TEXT,
            suroviny TEXT,
            postup TEXT,
            cas_min INTEGER,
            image_path TEXT,
            tags TEXT
        )
    """)

    c.execute("PRAGMA table_info(recepty)")
    columns = [col[1] for col in c.fetchall()]

    if "tags" not in columns:
        c.execute("ALTER TABLE recepty ADD COLUMN tags TEXT")
    conn.commit()
    
    try:
        c.execute("ALTER TABLE recepty ADD COLUMN cas_min INTEGER")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE recepty ADD COLUMN image_path TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    c.execute("SELECT id, cas FROM recepty WHERE cas_min IS NULL")
    rows = c.fetchall()
    for rid, cas_txt in rows:
        if cas_txt is None:
            continue
        m = re.search(r"\d+", str(cas_txt))
        if m:
            c.execute("UPDATE recepty SET cas_min=? WHERE id=?", (int(m.group(0)), rid))
    conn.commit()
    conn.close()    

def add_recept(nazev, cas_min, suroviny, postup, image_path=None, tags=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cas_min = int(cas_min) if str(cas_min).strip() != "" else None
    cas_txt = f"{cas_min}" if cas_min is not None else ""

    c.execute(
        "INSERT INTO recepty (nazev, cas, cas_min, suroviny, postup, image_path, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nazev, cas_txt, cas_min, suroviny, postup, image_path, tags),
    )
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return rid

def get_recepty():
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT id, nazev, cas_min FROM recepty ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

def get_recept(rid):
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT * FROM recepty WHERE id = ?", (rid,))
    data = c.fetchone()
    conn.close()
    return data

def update_recept(rid, nazev, cas_min, suroviny, postup, image_path=None, tags=None):
    conn = _connect()
    c = conn.cursor()
    cas_min = int(cas_min) if str(cas_min).strip() != "" else None
    cas_txt = f"{cas_min}" if cas_min is not None else ""
    c.execute(
        "UPDATE recepty SET nazev=?, cas=?, cas_min=?, suroviny=?, postup=?, image_path=?, tags=? WHERE id=?", 
        (nazev, cas_txt, cas_min, suroviny, postup, image_path, tags, rid),
    )
    conn.commit()
    conn.close()

def delete_recept(rid):
    conn = _connect()
    c = conn.cursor()

    c.execute("SELECT image_path FROM recepty WHERE id=?", (rid,))
    row = c.fetchone()
    image_path = row[0] if row else None

    c.execute("DELETE FROM recepty WHERE id=?", (rid,))
    conn.commit()
    conn.close()

    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except OSError:
            pass

def search_recepty(text, mode="nazev", time_cmp="le"):
    conn = _connect()
    c = conn.cursor()

    if mode == "cas":
        try:
            val = int(text)
        except ValueError:
            conn.close()
            return []
        
        if time_cmp == "eq":
            c.execute(
                "SELECT id, nazev, cas_min FROM recepty WHERE cas_min = ? ORDER BY id DESC",
                (val,),
            )    
        else:
            c.execute(
                "SELECT id, nazev, cas_min FROM recepty WHERE cas_min <= ? ORDER BY id DESC",
                (val,),
            )

        data = c.fetchall()
        conn.close()
        return data
    else:
        pattern = f"%{text}%"
        if mode == "suroviny":
            c.execute(
                "SELECT id, nazev, cas_min FROM recepty WHERE suroviny LIKE ? ORDER BY id DESC",
                (pattern,),
            )
        elif mode == "tags":
            c.execute(
                "SELECT id, nazev, cas_min FROM recepty WHERE tags LIKE ? ORDER BY id DESC",
                (pattern,),
            )
        else:
            c.execute(
                "SELECT id, nazev, cas_min FROM recepty WHERE nazev LIKE ? ORDER BY id DESC",
                (pattern,),
            )   
        data = c.fetchall()
        conn.close()
        return data
    
def save_image_for_recipe(rid, source_path):
    if not source_path:
        return None
    
    os.makedirs(IMG_DIR, exist_ok=True)

    ext = os.path.splitext(source_path)[1].lower()
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
        ext = ".png"

    dest = os.path.join(IMG_DIR, f"recept_{rid}{ext}")

    src_abs = os.path.abspath(source_path)
    dest_abs = os.path.abspath(dest)

    if src_abs == dest_abs:
        return dest
    
    shutil.copy2(source_path, dest)
    return dest    