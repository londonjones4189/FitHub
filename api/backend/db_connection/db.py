import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class DB:
    def __init__(self):
        self.db = None

    def get_db(self):
        if self.db is None:
            self.db = mysql.connector.connect(
                host=os.getenv('MYSQL_HOST', 'db'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_ROOT_PASSWORD'),
                database=os.getenv('MYSQL_DATABASE')
            )
        return self.db

db = DB()