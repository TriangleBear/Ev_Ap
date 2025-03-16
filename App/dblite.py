import datetime
from icecream import ic
from sqlite_db import SQLiteDB
from cloud_db import CloudDB
import threading
import queue
import time

# Global variable to store the current database instance
current_db_instance = None
# Thread-safe queue for database operations
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
        created_on = datetime.datetime.now().strftime('%Y-%m-%d')
        try:
            with DBActions.get_db_instance().get_db_connection(timeout=5) as conn:
                cursor = conn.cursor()
                sql = """INSERT INTO Members (rfid, memberid, name, student_num, program, year, date_registered) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (rfid, memberid, name, student_num, program, year, created_on))
                conn.commit()
            return 0
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return -1

    @staticmethod
    def member_exists(rfid):
        try:
            with DBActions.get_db_instance().get_db_connection() as conn:
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
            db_instance = DBActions.get_db_instance()
            with db_instance.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Different query based on database type
                if db_instance.use_cloud:
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    # MySQL returns tuples with the table name as the first element
                    return [table[0] for table in tables if table[0] != 'Members']
                else:
                    # SQLite query
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    # Filter out 'Members' table
                    return [table[0] for table in tables if table[0] not in ['Members', 'sqlite_sequence']]
        except Exception as e:
            ic(e)
            return []

    @staticmethod
    def create_event_table(table_name):
        table_name = table_name.replace(" ", "_")
        try:
            db_instance = DBActions.get_db_instance()
            with db_instance.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Different SQL based on database type
                if db_instance.use_cloud:
                    # MySQL syntax
                    sql = f"""CREATE TABLE IF NOT EXISTS `{table_name}` (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        rfid TEXT NOT NULL,
                        memberid TEXT NOT NULL,
                        student_num TEXT NOT NULL,
                        name TEXT NOT NULL,
                        attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )"""
                else:
                    # SQLite syntax
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
            return -1

    @staticmethod
    def fetch_table_data(table_name):
        try:
            with DBActions.get_db_instance().get_db_connection() as conn:
                cursor = conn.cursor()
                if table_name == 'Members':
                    sql = "SELECT DISTINCT rfid, memberid, name, student_num, date_registered FROM Members"
                else:
                    sql = f"SELECT DISTINCT memberid, name, student_num, attendance_time FROM {table_name}"
                cursor.execute(sql)
                result = cursor.fetchall()
            return result if result else []
        except Exception as e:
            ic(e)
            return []

    @staticmethod
    def fetch_table_data_async(table_name, callback=None):
        """Non-blocking version of fetch_table_data that runs in background thread"""
        def _fetch_worker():
            try:
                with DBActions.get_db_instance().get_db_connection(timeout=5) as conn:
                    cursor = conn.cursor()
                    if table_name == 'Members':
                        sql = "SELECT DISTINCT rfid, memberid, name, student_num, date_registered FROM Members"
                    else:
                        sql = f"SELECT DISTINCT memberid, name, student_num, attendance_time FROM {table_name}"
                    cursor.execute(sql)
                    result = cursor.fetchall()
                
                if callback:
                    callback(result if result else [])
                return result if result else []
            except Exception as e:
                ic(e)
                if callback:
                    callback([])
                return []
                
        thread = threading.Thread(target=_fetch_worker)
        thread.daemon = True
        thread.start()
        return thread

    @staticmethod
    def fetch_point_data(table_name):
        try:
            with DBActions.get_db_instance().get_db_connection() as conn:
                cursor = conn.cursor()
                sql = f"SELECT name, points FROM {table_name}"
                cursor.execute(sql)
                result = cursor.fetchall()
            return [{'name': row['name'], 'points': row['points']} for row in result]
        except Exception as e:
            ic(e)
            return []

    @staticmethod
    def attendance_member_event(table_name, rfid):
        try:
            member = DBActions.member_exists(rfid)
            if not member:
                raise ValueError("No member found with the given RFID")
            memberid = member['memberid']
            name = member['name']
            student_num = member['student_num']

            with DBActions.get_db_instance().get_db_connection() as conn:
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
            with DBActions.get_db_instance().get_db_connection() as conn:
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
            with DBActions.get_db_instance().get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "UPDATE Members SET points = points + ? WHERE rfid = ?"
                cursor.execute(sql, (points, rfid))
                conn.commit()
                ic(f"Added {points} points to RFID {rfid}")  # Debugging line to confirm points addition
            return 0
        except Exception as e:
            ic(e)
            return -1

    @staticmethod
    def get_member_points(rfid):
        try:
            with DBActions.get_db_instance().get_db_connection() as conn:
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
            with DBActions.get_db_instance().get_db_connection() as conn:
                cursor = conn.cursor()
                sql = "UPDATE Members SET points = points - ? WHERE rfid = ?"
                cursor.execute(sql, (points, rfid))
                conn.commit()
            return 0
        except Exception as e:
            ic(e)
            return -1

    @staticmethod
    def member_attended_event(table_name, rfid):
        try:
            with DBActions.get_db_instance().get_db_connection() as conn:
                cursor = conn.cursor()
                sql = f"SELECT COUNT(*) FROM {table_name} WHERE rfid = ?"
                cursor.execute(sql, (rfid,))
                result = cursor.fetchone()
            return result[0] > 0
        except Exception as e:
            ic(e)
            return False


class Database:
    def __init__(self, use_cloud=False, cloud_user=None, cloud_password=None, app=None):
        self.use_cloud = use_cloud
        self.cloud_user = cloud_user
        self.cloud_password = cloud_password
        self.app = app
        self.db = CloudDB(cloud_user, cloud_password, app) if use_cloud else SQLiteDB()
        self.initialization_complete = False
        
        # Set this instance as the current one
        DBActions.set_db_instance(self)

    def get_db_connection(self, timeout=None):
        if timeout is not None and self.use_cloud:
            return self.db.get_db_connection(timeout)
        return self.db.get_db_connection()

    def initialize_db(self, timeout=None):
        """Initialize the database with optional timeout"""
        start_time = time.time()
        try:
            if self.app:
                self.app.loading_status.configure(text="Creating database tables...")
            self.db.initialize_db(timeout)
            self.initialization_complete = True
            if self.app:
                elapsed = time.time() - start_time
                ic(f"Database initialization completed in {elapsed:.2f} seconds")
        except Exception as e:
            ic(f"Database initialization failed: {str(e)}")
            raise

    def db_exists(self):
        return self.db.db_exists()

    def backup_cloud_to_sqlite(self):
        if self.use_cloud:
            sqlite_db = SQLiteDB()
            self.db.backup_cloud_to_sqlite(sqlite_db)

# Don't initialize database at module import time
db = None
