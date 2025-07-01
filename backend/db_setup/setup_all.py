import json
import os
import sys
import pymongo
import mysql.connector
from mysql.connector import Error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger import get_logger
from utils.error_handler import DatabaseConnectionError, SetupError

from sqlite.init_sqlite import create_tables as create_sqlite_tables

from nosql.init_mongo import init_mongodb_collections


logger = get_logger('setup_all')

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'configs', 'db_config.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        logger.info("Loaded DB config successfully.")
        return config
    except Exception as e:
        logger.error("Failed to load DB config.")
        raise SetupError(f"Could not load DB config: {e}")

def connect_mysql(config):
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        if conn.is_connected():
            logger.info("Connected to MySQL successfully.")
            return conn
    except Error as e:
        logger.error(f"MySQL connection failed: {e}")
        raise DatabaseConnectionError("MySQL connection error.")

def connect_mongodb(config):
    try:
        mongo_uri = f"mongodb://{config['host']}:{config['port']}/"
        client = pymongo.MongoClient(mongo_uri)
        db = client[config['database']]
        logger.info("Connected to MongoDB successfully.") 
        return db
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise DatabaseConnectionError("MongoDB connection error.")
    
def run_sql_scripts(conn):
    cursor = conn.cursor()
    sql_dir = os.path.join(os.path.dirname(__file__), 'sql')

    for filename in ['admin_table.sql', 'host_participant_table.sql']:
        path = os.path.join(sql_dir, filename)
        try:
            with open(path, 'r') as f:
                script = f.read()
                cursor.execute(script)
                logger.info(f"Executed {filename} successfully.")
        except Exception as e:
            logger.error(f"Failed to execute {filename}: {e}")
    conn.commit()
    cursor.close()


def main():
    try:
        config = load_config()

        # Extract DB configs
        mysql_conf = config['mysql']
        mongo_conf = config['mongodb']
        mongo_uri = f"mongodb://{mongo_conf['host']}:{mongo_conf['port']}/"
        mongo_db_name = mongo_conf['database']

        # Step 1: Setup MySQL
        mysql_conn = connect_mysql(mysql_conf)
        run_sql_scripts(mysql_conn)
        mysql_conn.close()

        # Step 2: Setup SQLite
        create_sqlite_tables()

        # Step 3: Setup MongoDB
        mongo_db = connect_mongodb(mongo_conf)
        init_mongodb_collections(mongo_uri, mongo_db_name)

        logger.info("Setup completed successfully.")

    except (DatabaseConnectionError, SetupError) as e:
        logger.error(f"Setup failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
