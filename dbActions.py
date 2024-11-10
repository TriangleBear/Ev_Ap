import datetime
from dbcloud import Database
from icecream import ic

class DBActions:
    @staticmethod
    def member_register(rfid, memberid, name, student_num, program, year):
        created_on = datetime.datetime.now()
        try:
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """INSERT INTO Members (rfid, memberid, name, student_num, program, year, date_registered) 
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (rfid, memberid, name, student_num, program, year, created_on.strftime('%Y-%m-%d')))
                    conn.commit()
            return 0
        except pymysql.ProgrammingError as e:
            ic(e)  # Debugging line to print the exception
            return -1
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return -1

    @staticmethod
    def member_exists(rfid):
        try:
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT memberid FROM Members WHERE rfid = %s"
                    cursor.execute(sql, (rfid,))
                    result = cursor.fetchone()
            return result
        except Exception as e:
            ic(e)  # Debugging line to print the exception
            return None

    # get all tables except Members Table
    @staticmethod
    def list_tables(db):
        try:
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SHOW TABLES"
                    cursor.execute(sql)
                    tables = cursor.fetchall()
            return [table for table in tables if table != 'Members']
        except Exception as e:
            ic(e)  # Debugging line to print the exception

    @staticmethod
    def create_event_table(table_name):
        table_name = table_name.replace(" ", "_")
        try:
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Create the table
                    sql = f"""CREATE TABLE `{table_name}` (
                                id INT auto_increment NOT NULL,
                                rfid INT NOT NULL,
                                memberid VARCHAR(50) NOT NULL,
                                student_num INT NOT NULL,
                                name VARCHAR(255) NOT NULL,
                                attendance_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                                CONSTRAINT {table_name}_PK PRIMARY KEY (id),
                                CONSTRAINT {table_name}MemberID_FK FOREIGN KEY (rfid) REFERENCES Members(rfid)
                            )"""
                    cursor.execute(sql)
                    conn.commit()
            return 0
        except Exception as e:
            ic(e)

    @staticmethod
    def fetch_table_data(table_name):
        if table_name == 'Members':
            try:
                with Database.get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        sql = f"SELECT DISTINCT memberid, name, student_num, date_registered FROM Members"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                return result
            except Exception as e:
                ic(e)
        elif table_name != 'Members':
            try:
                with Database.get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        sql = f"SELECT DISTINCT memberid, name, student_num, attendance_time FROM {table_name}"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                return result
            except Exception as e:
                ic(e)

    @staticmethod
    def attendance_member_event(table_name, rfid):
        try:
            name = DBActions.member_exists(rfid)['name']
            student_num = DBActions.member_exists(rfid)['student_num']
            memberid = DBActions.member_exists(rfid)['memberid']
            if not name:
                raise ValueError(f"No member found with memberid: {memberid}")
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = f"INSERT INTO {table_name} (rfid, memberid, name, student_num) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (rfid, memberid, name, student_num))
                    conn.commit()
            return 0
        except Exception as e:
            ic(e)
            return -1

    def member_exists(rfid):
        try:
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT rfid, memberid, name, student_num FROM Members WHERE rfid = %s"
                    cursor.execute(sql, (rfid,))
                    result = cursor.fetchone()
            return result
        except Exception as e:
            ic(e)
            return None

    @staticmethod
    def get_member_name(rfid):
        try:
            with Database.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT name FROM Members WHERE rfid = %s"
                    cursor.execute(sql, (rfid,))
                    result = cursor.fetchone()
            return result['name'] if result else None
        except Exception as e:
            ic(e)
            return None
