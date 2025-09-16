from pymongo import MongoClient
from dotenv import load_dotenv
import time
import os 



MONGO_URL=os.getenv("MONGO_URL")
MONGO_HOST=os.getenv("MONGO_HOST")
MONGO_PORT=os.getenv("MONGO_PORT")
MONGO_DB_NAME=os.getenv("MONGO_DB_NAME")
MONGO_INITDB_ROOT_USERNAME=os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD=os.getenv("MONGO_INITDB_ROOT_PASSWORD")

def read_data(user_id: str, file_name: str) -> list:

    print(f"[MONGO FETCHER {user_id}] Starting fetch for file '{file_name}'...")

    with MongoClient(f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource=admin") as client:
        user_db = client[user_id]
        data_collection = user_db[file_name]
        print(user_db)
        print(data_collection)
        query = {"filename": file_name}

        start_time = time.time()
        
        cursor = data_collection.find(query)
        documents = list(cursor)
        duration = time.time() - start_time
        
        record_count = len(documents)
        print(f"[MONGO FETCHER {user_id}] Finished. Found {record_count} records for '{file_name}' in {duration:.4f} seconds.")
        
        return documents
