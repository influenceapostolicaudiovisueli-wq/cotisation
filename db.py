import sqlite3
import os

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # permet d'utiliser dict-like
    return conn

def init_db():
    # créer le dossier si besoin
    if not os.path.exists(DB_NAME):
        conn = get_db()
        cur = conn.cursor()

        # TABLE MEMBRES
        cur.execute("""
        CREATE TABLE membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            tel TEXT,
            montant INTEGER NOT NULL,
            actif INTEGER DEFAULT 1,
            date TEXT
        )
        """)

        # TABLE COTISATIONS
        cur.execute("""
        CREATE TABLE cotisations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            membre_id INTEGER,
            montant INTEGER,
            periode TEXT,
            date TEXT,
            FOREIGN KEY (membre_id) REFERENCES membres(id)
        )
        """)

        # TABLE DEPENSES
        cur.execute("""
        CREATE TABLE depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            motif TEXT,
            montant INTEGER,
            par TEXT,
            date TEXT
        )
        """)

        conn.commit()
        conn.close()
