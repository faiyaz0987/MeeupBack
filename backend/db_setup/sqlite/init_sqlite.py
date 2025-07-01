import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'backup.db')

def create_tables():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Admin table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                uid TEXT PRIMARY KEY,
                full_name TEXT,
                address TEXT,
                mobile_num TEXT,
                email TEXT,
                valid_id_numbers TEXT,       -- Stored as JSON string
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT,             -- Stored as JSON string
                password TEXT,
                username TEXT UNIQUE
            );
        ''')

        # Host/Participant table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS host_participant (
                uid TEXT PRIMARY KEY,
                full_name TEXT,
                email TEXT,
                mobile_num TEXT,
                address TEXT,
                location TEXT,
                hosting_addresses TEXT,      -- Stored as JSON string
                locality TEXT,               -- Stored as JSON string
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT,
                password TEXT,
                username TEXT UNIQUE,
                ranged_id INTEGER UNIQUE
            );
        ''')

        conn.commit()
        print("[SQLite] Tables created successfully.")
    except Exception as e:
        print(f"[SQLite] Error creating tables: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()
