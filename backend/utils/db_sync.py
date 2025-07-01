import json
import sqlite3
import pymongo
import mysql.connector
from mysql.connector import Error
from utils.logger import get_logger
from utils.error_handler import SyncError

logger = get_logger('db_sync')

class DBSync:
    def __init__(self, mysql_conf, sqlite_path, mongo_conf):
        try:
            # MySQL
            self.mysql_conn = mysql.connector.connect(**mysql_conf)
            self.mysql_cursor = self.mysql_conn.cursor()

            # SQLite
            self.sqlite_conn = sqlite3.connect(sqlite_path)
            self.sqlite_cursor = self.sqlite_conn.cursor()

            # MongoDB
            mongo_uri = f"mongodb://{mongo_conf['host']}:{mongo_conf['port']}/"
            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.mongo_db = self.mongo_client[mongo_conf['database']]

            self.sql = self.mysql_conn
            self.mongo = self.mongo_db

            logger.info("DB connections initialized in sync module.")

        except Exception as e:
            logger.error(f"Error initializing DB sync connections: {e}")
            raise SyncError("Failed to connect to one or more databases.")

    def insert_admin(self, data):
        try:
            # MySQL insert
            mysql_query = """
            INSERT INTO admin (uid, full_name, address, mobile_num, email,
                valid_id_numbers, created_at, updated_at, password, username)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.mysql_cursor.execute(mysql_query, (
                data['uid'],
                data['full_name'],
                data['address'],
                data['mobile_num'],
                data['email'],
                json.dumps(data['valid_id_numbers']),
                data['created_at'],
                json.dumps(data['updated_at']),
                data['password'],
                data['username']
            ))
            self.mysql_conn.commit()

            # SQLite insert
            sqlite_query = """
            INSERT INTO admin (uid, full_name, address, mobile_num, email,
                valid_id_numbers, created_at, updated_at, password, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.sqlite_cursor.execute(sqlite_query, (
                data['uid'],
                data['full_name'],
                data['address'],
                data['mobile_num'],
                data['email'],
                json.dumps(data['valid_id_numbers']),
                data['created_at'],
                json.dumps(data['updated_at']),
                data['password'],
                data['username']
            ))
            self.sqlite_conn.commit()

            # MongoDB insert
            self.mongo_db['admin_docs'].insert_one(data)

            logger.info(f"Admin user {data['uid']} synced across all DBs.")

        except Exception as e:
            logger.error(f"Failed to sync admin record: {e}")
            raise SyncError("Error during admin DB sync.")
        

    def insert_host_participant(self, data):
        try:
            # MySQL insert
            mysql_query = """
            INSERT INTO host_participant (
                uid, full_name, email, mobile_num, address, location,
                hosting_addresses, locality, created_at, updated_at,
                password, username, ranged_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.mysql_cursor.execute(mysql_query, (
                data['uid'],
                data['full_name'],
                data['email'],
                data['mobile_num'],
                data['address'],
                data['location'],
                json.dumps(data['hosting_addresses']),
                json.dumps(data['locality']),
                data['created_at'],
                json.dumps(data['updated_at']),
                data['password'],
                data['username'],
                data['ranged_id']
            ))
            self.mysql_conn.commit()

            # SQLite insert
            sqlite_query = """
            INSERT INTO host_participant (
                uid, full_name, email, mobile_num, address, location,
                hosting_addresses, locality, created_at, updated_at,
                password, username, ranged_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.sqlite_cursor.execute(sqlite_query, (
                data['uid'],
                data['full_name'],
                data['email'],
                data['mobile_num'],
                data['address'],
                data['location'],
                json.dumps(data['hosting_addresses']),
                json.dumps(data['locality']),
                data['created_at'],
                json.dumps(data['updated_at']),
                data['password'],
                data['username'],
                data['ranged_id']
            ))
            self.sqlite_conn.commit()

            # MongoDB insert
            self.mongo_db['host_participant_docs'].insert_one(data)

            logger.info(f"Host/Participant {data['uid']} synced across all DBs.")

        except Exception as e:
            logger.error(f"Failed to sync host_participant record: {e}")
            raise SyncError("Error during host_participant DB sync.")


    def close_all(self):
        try:
            self.mysql_cursor.close()
            self.mysql_conn.close()
            self.sqlite_cursor.close()
            self.sqlite_conn.close()
            self.mongo_client.close()
            logger.info("Closed all DB connections.")
        except Exception as e:
            logger.warning(f"Error closing DBs: {e}")
