import datetime
import sqlite3
from icecream import ic
from dblite import Database as DBActionsLite

class DBActions:
    @staticmethod
    def member_register(memberid, name, student_num, program, year):
        created_on = datetime.datetime.now()
        try:
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            # Create the table if it doesn't exist
            cursor.execute("CREATE TABLE IF NOT EXISTS Members (id INTEGER PRIMARY KEY AUTOINCREMENT, memberid INTEGER PRIMARY KEY, name TEXT, student_num INTEGER, program TEXT, year TEXT, date_registered TEXT)")
            sql = """INSERT INTO Members (memberid, name, student_num, program, year, date_registered) 
                     VALUES (?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, (memberid, name, student_num, program, year, created_on.strftime('%Y-%m-%d')))
            conn.commit()
            conn.close()
            return 0
        except sqlite3.Error as e:
            ic(e)  # Debugging line to print the exception
            return -1
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return -1

    @staticmethod
    def member_exists(memberid):
        try:
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT * FROM Members WHERE memberid = ?"
            cursor.execute(sql, (memberid,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return None

    # get all tables except Members Table
    @staticmethod
    def list_tables(db):
        try:
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT name FROM sqlite_master WHERE type='table' AND name!='Members'"
            cursor.execute(sql)
            tables = cursor.fetchall()
            conn.close()
            return [table[0] for table in tables]
        except Exception as e:
            ic(e)  # Debugging line to print the exception

    @staticmethod
    def create_event_table(table_name):
        table_name = table_name.replace(" ", "_")
        try:
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            # Create the table
            sql = f"""CREATE TABLE IF NOT EXISTS `{table_name}` (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        memberid INTEGER NOT NULL,
                        student_num INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        attendance_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (memberid) REFERENCES Members(memberid)
                    )"""
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return 0
        except Exception as e:
            ic(e)

    @staticmethod
    def fetch_table_data(table_name):
        try:
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            sql = f"SELECT * FROM {table_name}"
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            ic(e)

    @staticmethod
    def attendance_member_event(table_name, memberid):
        try:
            name = DBActionsLite.member_exists(memberid)['name']
            student_num = DBActionsLite.member_exists(memberid)['student_num']
            if not name:
                raise ValueError(f"No member found with memberid: {memberid}")
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            sql = f"INSERT INTO {table_name} (memberid, name, student_num) VALUES (?, ?, ?)"
            cursor.execute(sql, (memberid, name, student_num))
            conn.commit()
            conn.close()
            return 0
        except Exception as e:
            ic(e)
            return -1

    @staticmethod
    def get_member_name(memberid):
        try:
            conn = DBActionsLite.get_db_connection()
            cursor = conn.cursor()
            sql = "SELECT name FROM Members WHERE memberid = ?"
            cursor.execute(sql, (memberid,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            ic(e)
            return None
