from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
import json

def init_mongodb_collections(mongo_uri, db_name):
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]

        # Ensure collections exist
        admin_coll = db['admin_docs']
        host_participant_coll = db['host_participant_docs']

        # Insert dummy if collections are empty
        if admin_coll.estimated_document_count() == 0:
            admin_coll.insert_one({"_init": True})
        if host_participant_coll.estimated_document_count() == 0:
            host_participant_coll.insert_one({"_init": True})

        print("[MongoDB] Collections ensured successfully.")
    except PyMongoError as e:
        print(f"[MongoDB] Error initializing collections: {e}")
