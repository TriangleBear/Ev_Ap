import sqlite3
import os

class Database:
    @staticmethod
    def get_db_connection():
        db_path = 'AHO_MEMBER.db'
        
        # Create the database file if it does not exist
        if not os.path.exists(db_path):
            open(db_path, 'w').close()
        
        ahodb = sqlite3.connect(db_path)
        ahodb.row_factory = sqlite3.Row
        
        return ahodb

    @staticmethod
    def initialize_db():
        conn = Database.get_db_connection()
        cursor = conn.cursor()
        # Create the table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memberid INTEGER,
                name TEXT,
                student_num INTEGER,
                program TEXT,
                year TEXT,
                date_registered TEXT
            )
        ''')
        conn.commit()
        conn.close()

# Initialize the database and create tables if they do not exist
Database.initialize_db()