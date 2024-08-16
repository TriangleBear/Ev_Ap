import pymysql
import pymysql.cursors
from creds import Credentials

class Database:
    def get_db_connection():
        ahodb = pymysql.connect(
            host=Credentials.host,
            user=Credentials.user,
            password=Credentials.password,
            db=Credentials.db,
            port=Credentials.port,
            cursorclass=pymysql.cursors.DictCursor,
        )
        return ahodb