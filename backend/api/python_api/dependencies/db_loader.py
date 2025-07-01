import sys
import os
import json

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from utils.db_sync import DBSync


_db_sync_instance = None

def get_db_sync():
    global _db_sync_instance
    if _db_sync_instance is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'configs', 'db_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)

        mysql_conf = config['mysql']
        mongo_conf = config['mongodb']
        sqlite_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'db_setup', 'sqlite', 'backup.db')

        _db_sync_instance = DBSync(mysql_conf, sqlite_path, mongo_conf)

    return _db_sync_instance
