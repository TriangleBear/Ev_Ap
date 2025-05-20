import sqlite3
import os
import time

class SQLiteDB:
    def get_db_connection(self, timeout=None):
        db_path = 'AHO_MEMBER.db'
        if not os.path.exists(db_path):
            open(db_path, 'w').close()
        
        # Apply timeout if specified
        if timeout is not None:
            ahodb = sqlite3.connect(db_path, timeout=timeout)
        else:
            ahodb = sqlite3.connect(db_path)
            
        ahodb.row_factory = sqlite3.Row
        return ahodb

    def initialize_db(self, timeout=None):
        conn = self.get_db_connection(timeout)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Members (
            rfid TEXT PRIMARY KEY,
            memberid TEXT,
            name TEXT,
            student_num TEXT,
            program TEXT,
            year TEXT,
            date_registered TEXT,
            points REAL DEFAULT 0
        )''')
        cursor.execute("PRAGMA table_info(Members)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'points' not in columns:
            cursor.execute("ALTER TABLE Members ADD COLUMN points REAL DEFAULT 0")
        conn.commit()
        conn.close()

    def db_exists(self):
        db_path = 'AHO_MEMBER.db'
        return os.path.exists(db_path)

    def fetch_all_data(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table[0]}")
            data[table[0]] = cursor.fetchall()
        conn.close()
        return data
