from pymongo import MongoClient
from dotenv import load_dotenv
import polars as pl
import numpy as np
import time
import io
import os
import uuid
load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

def insert_data(user_id: str, filename: str, file_content: bytes):
    client = None
    start_total_time = time.time()
    print(f"[MONGO WORKER {user_id}] Starting bulk upload of '{filename}'...")
    
    try:
        client = MongoClient(f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}?authSource=admin")
        user_db = client[user_id]
        filename_collection = user_db[filename]

        df = pl.read_csv(io.BytesIO(file_content))
        # df = df.replace({np.nan: None})
        data_records = df.to_dicts()
        total_items = len(data_records)

        if total_items == 0:
            print(f"[MONGO WORKER {user_id}] No records to upload.")
            return 0

        documents_to_insert = [
            {
                "upload_id": f"upload_{user_id}_{time.time()}",
                "user_id": f"{user_id}",
                "filename": filename,
                **record 
            }
            for record in data_records
        ]
        result = filename_collection.insert_many(documents_to_insert)

        total_duration = time.time() - start_total_time
        
        print(f"[MONGO WORKER {user_id}] Finished bulk upload.")
        print(f"  - Summary for Worker {user_id}:")
        print(f"    - Total items inserted: {len(result.inserted_ids)}")
        print(f"    - Total time taken: {total_duration:.2f} seconds")

        return len(result.inserted_ids)
    finally:
        if client:
            client.close()
            
            
            