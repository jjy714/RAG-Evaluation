from pymongo import MongoClient
from dotenv import load_dotenv
import polars as pl
import numpy as np
import time
import io
import os

load_dotenv()

MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_URL = f"mongodb://localhost:{MONGO_PORT}"
MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")


def insert_data(worker_id: int, filename: str, file_content: bytes):
    client = None
    start_total_time = time.time()
    print(f"[MONGO WORKER {worker_id}] Starting bulk upload of '{filename}'...")
    
    try:
        client = MongoClient(MONGO_URL, username=MONGO_INITDB_ROOT_USERNAME, password=MONGO_INITDB_ROOT_PASSWORD)
        datasets_db = client.datasets_db
        datasets_collection = datasets_db["datasets_collection"]

        df = pl.read_csv(io.BytesIO(file_content))
        # df = df.replace({np.nan: None})
        data_records = df.to_dict(orient="records")
        total_items = len(data_records)

        if total_items == 0:
            print(f"[MONGO WORKER {worker_id}] No records to upload.")
            return 0

        documents_to_insert = [
            {
                "upload_id": f"upload_{worker_id}_{time.time()}",
                "user_id": f"user_{worker_id}",
                "filename": filename,
                **record 
            }
            for record in data_records
        ]
        result = datasets_collection.insert_many(documents_to_insert)

        total_duration = time.time() - start_total_time
        
        print(f"[MONGO WORKER {worker_id}] Finished bulk upload.")
        print(f"  - Summary for Worker {worker_id}:")
        print(f"    - Total items inserted: {len(result.inserted_ids)}")
        print(f"    - Total time taken: {total_duration:.2f} seconds")

        return len(result.inserted_ids)
    finally:
        if client:
            client.close()