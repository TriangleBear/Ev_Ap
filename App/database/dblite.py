import datetime
from icecream import ic
from .sqlite_db import SQLiteDB
from .sheet_db import SheetDB
from .config import get_db_mode, get_gsheet_api_url
import threading
import queue
import time

current_db_instance = None
db_operation_queue = queue.Queue()


class DBActions:
    @staticmethod
    def set_db_instance(db_instance):
        global current_db_instance
        current_db_instance = db_instance

    @staticmethod
    def get_db_instance():
        global current_db_instance
        if current_db_instance is None:
            current_db_instance = Database()
        return current_db_instance

    @staticmethod
    def member_register(rfid, memberid, name, student_num, program, year):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.member_register(rfid, memberid, name, student_num, program, year)
        created_on = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            with db.get_db_connection(timeout=5) as conn:
                cursor = conn.cursor()
                sql = """INSERT INTO Members (rfid, memberid, name, student_num, program, year, date_registered) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (rfid, memberid, name, student_num, program, year, created_on))
                conn.commit()
            return 0
        except Exception as e:
            ic(f"Error registering member: {e}")
            return -1

    @staticmethod
    def member_exists(rfid):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.member_exists(rfid)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT memberid, name, student_num FROM Members WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result if result else None
        except Exception as e:
            ic(f"Error checking member: {e}")
            return None

    @staticmethod
    def list_tables():
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.list_tables()
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return [table[0] for table in tables if table[0] not in ['Members', 'sqlite_sequence']]
        except Exception as e:
            ic(f"Error listing tables: {e}")
            return []

    @staticmethod
    def create_event_table(table_name):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.create_event_table(table_name)
        table_name = table_name.replace(" ", "_")
        try:
            with db.get_db_connection() as conn:
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
            ic(f"Error creating table: {e}")
            return -1

    @staticmethod
    def fetch_table_data(table_name):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.fetch_table_data(table_name)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                if table_name == 'Members':
                    sql = "SELECT DISTINCT rfid, memberid, name, student_num, date_registered FROM Members"
                else:
                    sql = f"SELECT DISTINCT memberid, name, student_num, attendance_time FROM {table_name}"
                cursor.execute(sql)
                result = cursor.fetchall()
            return result if result else []
        except Exception as e:
            ic(f"Error fetching data: {e}")
            return []

    @staticmethod
    def fetch_table_data_async(table_name, callback=None):
        def _fetch_worker():
            try:
                result = DBActions.fetch_table_data(table_name)
                if callback:
                    callback(result)
            except Exception as e:
                ic(f"Error in async fetch: {e}")
                if callback:
                    callback([])
        thread = threading.Thread(target=_fetch_worker)
        thread.daemon = True
        thread.start()
        return thread

    @staticmethod
    def attendance_member_event(table_name, rfid):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.attendance_member_event(table_name, rfid)
        try:
            member = DBActions.member_exists(rfid)
            if not member:
                raise ValueError("No member found with the given RFID")
            memberid = member['memberid']
            name = member['name']
            student_num = member['student_num']

            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = f"INSERT INTO {table_name} (rfid, memberid, name, student_num) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (rfid, memberid, name, student_num))
                conn.commit()
            return 0
        except Exception as e:
            ic(f"Error recording attendance: {e}")
            return -1

    @staticmethod
    def scan_attendance(table_name, rfid):
        """Batched scan: member_exists + check_attended + record in one call."""
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.scan_attendance(table_name, rfid)
        member = DBActions.member_exists(rfid)
        if not member:
            return {'success': False, 'error': 'RFID number not found'}
        attended = DBActions.member_attended_event(table_name, rfid)
        if attended:
            return {'success': True, 'attended': True}
        result = DBActions.attendance_member_event(table_name, rfid)
        return {'success': result == 0, 'attended': False}

    @staticmethod
    def get_member_name(rfid):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.get_member_name(rfid)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "SELECT name FROM Members WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result['name'] if result else None
        except Exception as e:
            ic(f"Error getting member name: {e}")
            return None

    @staticmethod
    def member_attended_event(table_name, rfid):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.member_attended_event(table_name, rfid)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                sql = f"SELECT COUNT(*) FROM {table_name} WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result[0] > 0
        except Exception as e:
            ic(f"Error checking attendance: {e}")
            return False

    @staticmethod
    def delete_event_table(table_name):
        db = DBActions.get_db_instance()
        if db.db_mode == 'gsheet':
            return db.sheet_db.delete_event(table_name)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                conn.commit()
            return 0
        except Exception as e:
            ic(f"Error deleting table: {e}")
            return -1


class Database:
    def __init__(self, app=None):
        self.app = app
        self.db_mode = get_db_mode()
        self.sqlite_db = SQLiteDB()
        self.sheet_db = SheetDB()
        self.initialization_complete = False

        api_url = get_gsheet_api_url()
        if api_url:
            self.sheet_db.set_api_url(api_url)

        DBActions.set_db_instance(self)

    def get_db_connection(self, timeout=None):
        if self.db_mode == 'gsheet':
            return self.sheet_db.get_db_connection(timeout)
        if timeout is not None:
            return self.sqlite_db.get_db_connection(timeout)
        return self.sqlite_db.get_db_connection()

    def initialize_db(self, timeout=None):
        start_time = time.time()
        try:
            if self.db_mode == 'gsheet':
                if self.app:
                    self.app.loading_status.configure(text="Connecting to Google Sheets...")
                self.sheet_db.initialize_db(timeout)
            else:
                if self.app:
                    self.app.loading_status.configure(text="Creating database tables...")
                self.sqlite_db.initialize_db(timeout)
            self.initialization_complete = True
            if self.app:
                elapsed = time.time() - start_time
                ic(f"Database initialization completed in {elapsed:.2f} seconds")
        except Exception as e:
            ic(f"Database initialization failed: {str(e)}")
            raise

    def db_exists(self):
        return self.sqlite_db.db_exists() or bool(self.sheet_db.api_url)

    def switch_mode(self, mode):
        if mode not in ('sqlite', 'gsheet'):
            raise ValueError("Mode must be 'sqlite' or 'gsheet'")
        self.db_mode = mode
        from .config import set_db_mode
        set_db_mode(mode)

db = None
