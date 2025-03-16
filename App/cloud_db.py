import pymysql
import sqlite3  # Add this import
from creds import CLOUD_DB_HOST, CLOUD_DB_PORT, CLOUD_DB_NAME
import customtkinter as CTk  # Add this import for CTKProgressBar

class CloudDB:
    def __init__(self, cloud_user, cloud_password, app):
        self.cloud_user = cloud_user
        self.cloud_password = cloud_password
        self.app = app  # Store the app object

    def get_db_connection(self):
        try:
            conn = pymysql.connect(
                host=CLOUD_DB_HOST,
                port=int(CLOUD_DB_PORT),
                database=CLOUD_DB_NAME,  # Use 'database' instead of 'dbname'
                user=self.cloud_user,
                password=self.cloud_password
            )
            return conn
        except pymysql.MySQLError as e:
            raise Exception(f"Error connecting to cloud database: {str(e)}")

    def initialize_db(self):
        conn = self.get_db_connection()
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
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='Members'")
        columns = [column[0] for column in cursor.fetchall()]
        required_columns = ['rfid', 'memberid', 'name', 'student_num', 'program', 'year', 'date_registered', 'points']
        for col in required_columns:
            if col not in columns:
                cursor.execute(f"ALTER TABLE Members ADD COLUMN {col} TEXT")
        conn.commit()
        conn.close()

    def db_exists(self):
        return True  # Assume cloud DB always exists

    def backup_cloud_to_sqlite(self, sqlite_db):
        cloud_conn = self.get_db_connection()
        sqlite_conn = sqlite_db.get_db_connection()

        cloud_cursor = cloud_conn.cursor()
        sqlite_cursor = sqlite_conn.cursor()

        # Always copy the Members table
        cloud_cursor.execute("SELECT * FROM Members")
        members = cloud_cursor.fetchall()

        sqlite_cursor.execute("DELETE FROM Members")
        for member in members:
            sqlite_cursor.execute(
                "INSERT INTO Members (rfid, memberid, name, student_num, program, year, date_registered, points) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                member
            )

        # Optionally copy other tables if they exist
        cloud_cursor.execute("SHOW TABLES")
        tables = cloud_cursor.fetchall()
        for table in tables:
            table_name = table[0]
            if table_name != 'Members':
                cloud_cursor.execute(f"SELECT * FROM {table_name}")
                rows = cloud_cursor.fetchall()

                sqlite_cursor.execute(f"DELETE FROM {table_name}")
                for row in rows:
                    placeholders = ', '.join(['?'] * len(row))
                    sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                    sqlite_cursor.execute(sql, row)

        sqlite_conn.commit()
        cloud_conn.close()
        sqlite_conn.close()

    def insert_data(self, table_name, data):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Ensure the Members table exists
        self.ensure_table_exists(cursor)
        
        # Initialize progress bar
        progress_bar = CTk.CTkProgressBar(self.app.root, mode='indeterminate')
        progress_bar.pack(side='bottom', pady=20)
        progress_bar.start()
        
        for row in data:
            if isinstance(row, sqlite3.Row):
                row = dict(row)  # Convert sqlite3.Row to dictionary
            placeholders = ', '.join(['%s'] * len(row))
            columns = ', '.join(row.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, list(row.values()))
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Duplicate entry error code
                    print(f"Duplicate entry found for {row}. Skipping insertion.")
                else:
                    raise e
        
        # Stop and hide progress bar after insertion
        progress_bar.stop()
        progress_bar.pack_forget()
        
        conn.commit()
        conn.close()

    def ensure_table_exists(self, cursor):
        # Initialize progress bar
        progress_bar = CTk.CTkProgressBar(self.app.root, mode='indeterminate')
        progress_bar.pack(side='bottom', pady=20)
        progress_bar.start()
        
        try:
            cursor.execute("SELECT 1 FROM Members LIMIT 1")
        except pymysql.err.ProgrammingError as e:
            if e.args[0] == 1146:  # Table does not exist error code
                print("Table 'Members' does not exist. Creating table...")
                cursor.execute("""
                    CREATE TABLE Members (
                        rfid TEXT PRIMARY KEY,
                        memberid TEXT,
                        name TEXT,
                        student_num TEXT,
                        program TEXT,
                        year TEXT,
                        date_registered TEXT,
                        points REAL DEFAULT 0
                    )
                """)
            else:
                 # Stop and hide progress bar after ensuring table exists
                progress_bar.stop()
                progress_bar.pack_forget()
                raise e
         # Stop and hide progress bar after ensuring table exists
        progress_bar.stop()
        progress_bar.pack_forget()

    def fetch_all_data(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        data = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name}")
            data[table_name] = cursor.fetchall()
        conn.close()
        return data


