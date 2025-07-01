import os
import json
from datetime import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.db_sync import DBSync
from utils.logger import get_logger

logger = get_logger("test_sync")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'configs', 'db_config.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def main():
    try:
        config = load_config()

        mysql_conf = config['mysql']
        mongo_conf = config['mongodb']
        sqlite_path = os.path.join(os.path.dirname(__file__), 'sqlite', 'backup.db')

        syncer = DBSync(mysql_conf, sqlite_path, mongo_conf)

        sample_admin = {
            "uid": "A001",
            "full_name": "Test Admin",
            "address": "123 Admin Lane",
            "mobile_num": "9999999999",
            "email": "admin@test.com",
            "valid_id_numbers": ["PAN1234", "AADHAR5678"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "password": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # SHA256(empty)
            "username": "admin_test"
        }

        syncer.insert_admin(sample_admin)
        print("[TEST] Admin record synced successfully.")

        sample_host = {
            "uid": "U001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "mobile_num": "8888888888",
            "address": "456 Participant Ave",
            "location": "Mumbai",
            "hosting_addresses": ["Room 1", "Flat 12B"],
            "locality": ["South Zone", "East Block"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "password": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "username": "john_doe",
            "ranged_id": 1001
        }

        syncer.insert_host_participant(sample_host)
        print("[TEST] Host/Participant record synced successfully.")


        syncer.close_all()

    except Exception as e:
        print(f"[TEST] Sync test failed: {e}")
        logger.error(f"Test sync failed: {e}")

if __name__ == "__main__":
    main()
