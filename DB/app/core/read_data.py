from pymongo import MongoClient
from dotenv import load_dotenv
import time
import os 



MONGO_URL=os.getenv("MONGO_URL")
MONGO_PORT=os.getenv("MONGO_PORT")
MONGO_INITDB_ROOT_USERNAME=os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD=os.getenv("MONGO_INITDB_ROOT_PASSWORD")

def read_data(worker_id: int, file_name: str) -> list:

    print(f"[MONGO FETCHER {worker_id}] Starting fetch for file '{file_name}'...")

    with MongoClient(MONGO_URL, username=MONGO_INITDB_ROOT_USERNAME, password=MONGO_INITDB_ROOT_PASSWORD) as client:
        datasets_db = client.datasets_db
        datasets_collection = datasets_db["datasets_collection"]
        query = {"filename": file_name}

        start_time = time.time()
        
        cursor = datasets_collection.find(query)
        documents = list(cursor)

        duration = time.time() - start_time
        
        record_count = len(documents)
        print(f"[MONGO FETCHER {worker_id}] Finished. Found {record_count} records for '{file_name}' in {duration:.4f} seconds.")
        
        return documents
