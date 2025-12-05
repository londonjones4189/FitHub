import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class DB:
    def __init__(self):
        self.db = None

    def get_db(self):
        if self.db is None or not self.db.is_connected():
            self.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'db'),
                user=os.getenv('MYSQL_USER', 'fithub'),
                password=os.getenv('MYSQL_PASSWORD', 'fithub'),
                database=os.getenv('MYSQL_DATABASE', 'fithub'),
                auth_plugin='mysql_native_password',
                autocommit=False
            )
        return self.db

db = DB()