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


def create_db(user_id: str):
    client = MongoClient(
        host="mongodb://0.0.0.0",
        port=MONGO_PORT,
        username=MONGO_INITDB_ROOT_USERNAME,
        password=MONGO_INITDB_ROOT_PASSWORD
        )
    print(client.list_database_names())
    db = client["new_db"]
    collection = db["new_collection"]
    print( db.list_collection_names())