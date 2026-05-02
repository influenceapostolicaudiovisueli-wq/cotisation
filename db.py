import sqlite3

def get_db():
    return sqlite3.connect("nexus.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS membres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        tel TEXT,
        montant REAL NOT NULL,
        actif INTEGER DEFAULT 1,
        date TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cotisations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        membre_id INTEGER,
        montant REAL,
        periode TEXT,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        motif TEXT,
        montant REAL,
        par TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()
