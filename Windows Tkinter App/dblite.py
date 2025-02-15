import datetime
from icecream import ic
import sqlite3
import os

class DBActions:
    @staticmethod
    def member_register(rfid, memberid, name, student_num, program, year):
        created_on = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = """INSERT INTO Members (rfid, memberid, name, student_num, program, year, date_registered) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (rfid, memberid, name, student_num, program, year, created_on))
                conn.commit()
            return 0
        except sqlite3.ProgrammingError as e:
            ic(e)  # Debugging line to print the exception
            return -1
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return -1

    @staticmethod
    def member_exists(rfid):
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT memberid, name, student_num FROM Members WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result if result else None
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return None

    @staticmethod
    def list_tables():
        try:
            with Database.get_db_connection() as conn:
                conn = Database.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
            # Filter out 'Members' table
            return [table[0] for table in tables if table[0] not in ['Members', 'sqlite_sequence']]
        except Exception as e:
            ic(e)
            return []

    @staticmethod
    def create_event_table(table_name):
        table_name = table_name.replace(" ", "_")
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = f"""CREATE TABLE IF NOT EXISTS `{table_name}` (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              rfid TEXT NOT NULL,
                              memberid TEXT NOT NULL,
                              student_num TEXT NOT NULL,
                              name TEXT NOT NULL,
                              attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              FOREIGN KEY (rfid) REFERENCES Members(rfid)
                          )"""
                cursor.execute(sql)
                conn.commit()
            return 0
        except Exception as e:
            ic(e)

    @staticmethod
    def fetch_table_data(table_name):
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                if table_name == 'Members':
                    sql = "SELECT DISTINCT rfid, memberid, name, student_num, date_registered FROM Members"
                else:
                    sql = f"SELECT DISTINCT memberid, name, student_num, attendance_time FROM {table_name}"
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except Exception as e:
            ic(e)

    @staticmethod
    def attendance_member_event(table_name, rfid):
        try:
            member = DBActions.member_exists(rfid)
            if not member:
                raise ValueError("No member found with the given RFID")
            memberid = member['memberid']
            name = member['name']
            student_num = member['student_num']

            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = f"INSERT INTO {table_name} (rfid, memberid, name, student_num) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (rfid, memberid, name, student_num))
                conn.commit()
            return 0
        except Exception as e:
            ic(e)
            return -1

    @staticmethod
    def get_member_name(rfid):
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT name FROM Members WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result['name'] if result else None
        except Exception as e:
            ic(e)
            return None

    @staticmethod
    def add_points(rfid, points):
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "UPDATE Members SET points = points + ? WHERE rfid = ?"
                cursor.execute(sql, (points, rfid))
                conn.commit()
            return 0
        except Exception as e:
            ic(e)
            return -1

    @staticmethod
    def get_member_points(rfid):
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT points FROM Members WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result['points'] if result else None
        except Exception as e:
            ic(e)
            return None

    @staticmethod
    def redeem_points(rfid, points):
        try:
            with Database.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "UPDATE Members SET points = points - ? WHERE rfid = ?"
                cursor.execute(sql, (points, rfid))
                conn.commit()
            return 0
        except Exception as e:
            ic(e)
            return -1


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
        # Add the points column if it doesn't exist
        cursor.execute("PRAGMA table_info(Members)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'points' not in columns:
            cursor.execute("ALTER TABLE Members ADD COLUMN points REAL DEFAULT 0")
        conn.commit()
        conn.close()

    @staticmethod
    def db_exists():
        db_path = 'AHO_MEMBER.db'
        # Check if the database file exists
        return os.path.exists(db_path)


# Initialize the database and create tables if they do not exist
Database.initialize_db()
