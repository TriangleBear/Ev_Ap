import pymysql
import sqlite3  # Add this import
import customtkinter as CTk  # Add this import for CTKProgressBar
import time

class CloudDB:
    def __init__(self, cloud_user, cloud_password, app):
        self.cloud_user = cloud_user
        self.cloud_password = cloud_password
        self.app = app  # Store the app object

    def get_db_connection(self, timeout=None):
        try:
            # Set connect_timeout if provided
            connect_timeout = timeout if timeout is not None else 30
            
            conn = pymysql.connect(
                host=CLOUD_DB_HOST,
                port=int(CLOUD_DB_PORT),
                database=CLOUD_DB_NAME,
                user=self.cloud_user,
                password=self.cloud_password,
                connect_timeout=connect_timeout  # Add connection timeout
            )
            return conn
        except pymysql.MySQLError as e:
            raise Exception(f"Error connecting to cloud database: {str(e)}")

    def initialize_db(self, timeout=None):
        start_time = time.time()
        conn = self.get_db_connection(timeout)
        cursor = conn.cursor()
        
        # Update progress indicator if available
        if self.app and hasattr(self.app, 'loading_status'):
            self.app.loading_status.configure(text="Creating Members table...")
            self.app.root.update()
            
        # Create Members table with timeout handling
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
        
        if self.app and hasattr(self.app, 'loading_status'):
            self.app.loading_status.configure(text="Checking columns...")
            self.app.root.update()
            
        # Check if all required columns exist
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
        # Show initialization message
        if self.app and hasattr(self.app, 'loading_status'):
            self.app.loading_status.configure(text=f"Inserting data into {table_name}...")
            self.app.root.update()
            
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Ensure the table exists
        self.ensure_table_exists(cursor, table_name)
        
        # Initialize progress bar with determinate mode
        rows_inserted = 0
        total_rows = len(data)
        
        if self.app and hasattr(self.app, 'progress_bar'):
            progress_bar = self.app.progress_bar
            progress_bar.set(0)
            self.app.root.update()
        
        # Process data in smaller batches
        for row in data:
            if isinstance(row, sqlite3.Row):
                row = dict(row)  # Convert sqlite3.Row to dictionary
            placeholders = ', '.join(['%s'] * len(row))
            columns = ', '.join(row.keys())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            try:
                cursor.execute(sql, list(row.values()))
                rows_inserted += 1
                
                # Update progress every 10 rows or so
                if rows_inserted % 10 == 0 and self.app and hasattr(self.app, 'progress_bar'):
                    self.app.progress_bar.set(rows_inserted / total_rows)
                    self.app.root.update()
                    
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Duplicate entry error code
                    print(f"Duplicate entry found for {row}. Skipping insertion.")
                else:
                    raise e
                    
        conn.commit()
        conn.close()
        
        # Set progress complete
        if self.app and hasattr(self.app, 'progress_bar'):
            self.app.progress_bar.set(1.0)
            self.app.root.update()

    def ensure_table_exists(self, cursor, table_name=None):
        # Check if it's the Members table
        if table_name is None or table_name.lower() == 'members':
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
                    raise e
        else:
            # For other tables
            try:
                cursor.execute(f"SELECT 1 FROM `{table_name}` LIMIT 1")
            except pymysql.err.ProgrammingError as e:
                if e.args[0] == 1146:  # Table does not exist error code
                    print(f"Table '{table_name}' does not exist. Creating table...")
                    cursor.execute(f"""
                        CREATE TABLE `{table_name}` (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            rfid TEXT NOT NULL,
                            memberid TEXT NOT NULL,
                            student_num TEXT NOT NULL,
                            name TEXT NOT NULL,
                            attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                else:
                    raise e

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


