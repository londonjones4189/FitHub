import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

class DB:
    def __init__(self):
        self.db = None

    def get_db(self):
        if self.db is None or not self.db.is_connected():
            connection_config = {
                'host': os.getenv("DB_HOST", "db"),
                'port': int(os.getenv("DB_PORT", 3306)),
                'user': os.getenv("DB_USER", "root"),
                'password': os.getenv("DB_PASSWORD", "1234"),
                'database': os.getenv("DB_NAME", "fithub"),
                'autocommit': False
            }
            
            self.db = mysql.connector.connect(**connection_config)
        return self.db

db = DB()
