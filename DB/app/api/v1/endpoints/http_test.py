import os
import time
import pandas as pd
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
import io

from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter
from pymongo import MongoClient
import numpy as np
# import psycopg2
# from psycopg2.extras import Json

# --- Configuration ---
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_URI = f"mongodb://{MONGO_HOST}:9017/"

# Create the FastAPI app instance
router = APIRouter()

# Create a single ThreadPoolExecutor to be reused by the router
# This is more efficient than creating one for each request.
executor = ThreadPoolExecutor(max_workers=50)


# --- Database Worker Functions (Synchronous/Blocking) ---
# These are the same functions from your previous script, slightly adapted.



            
            




# --- API Endpoints ---




@router.get("/find/mongo/{file_name}")
async def read_from_mongo(file_name: str):
    try:
        loop = asyncio.get_running_loop()

        record_count = await loop.run_in_executor(
            executor, mongo_dataset_fetcher, int(time.time()),file_name
        )

        return {"message": f"Successfully read {file_name} with {record_count} records from MongoDB."}

    except Exception as e:
        print("ERROR during read_from_mongo:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
