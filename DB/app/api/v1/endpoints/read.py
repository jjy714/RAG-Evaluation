from app.core import read_data
from fastapi import APIRouter, HTTPException, UploadFile, File
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from bson import ObjectId 
import traceback
import time
import asyncio

router = APIRouter()


# Create the executor once, outside the request function for efficiency
executor = ThreadPoolExecutor(max_workers=10)

def serialize_mongo_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Helper function to convert MongoDB's ObjectId to a string for JSON serialization.
    """
    if not isinstance(docs, list):
        return []
        
    for doc in docs:
        if "_id" in doc and isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])
    return docs



@router.get("/{file_name}")
async def read(user_id: str, file_name: str):
    """
    Reads data for a given user and filename from the database and returns
    the data as the API response.
    """
    print(f"Received request for filename: '{file_name}' and user_id: '{user_id}'")
    try:
        loop = asyncio.get_running_loop()

        # 1. Store the result in a more descriptive variable name.
        #    This variable will hold the list of documents from the DB.
        retrieved_records = await loop.run_in_executor(
            executor, read_data, user_id, file_name
        )

        # 2. Serialize the data to make it JSON-compatible.
        json_compatible_records = serialize_mongo_docs(retrieved_records)

        # 3. THE FIX: Return the actual data.
        #    FastAPI will automatically convert this list of dictionaries
        #    into a JSON array in the HTTP response.
        return {"status": "ok", "records": json_compatible_records}

    except Exception as e:
        print(f"ERROR during read_from_mongo: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))