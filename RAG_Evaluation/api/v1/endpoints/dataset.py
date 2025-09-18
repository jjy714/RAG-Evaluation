from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from schema import BenchmarkRequest
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from cache_redis import get_cache, set_cache
from pathlib import Path 
from core import RedisSessionHandler
import logging
import httpx
import json
import os

env_path = Path(".").parent.parent
load_dotenv(env_path)

## STEP 2. GET DATASET !!

DB_PORT= os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
router = APIRouter()


def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.post("/get-benchmark-dataset")
async def get_benchmark_dataset(request: BenchmarkRequest):
    session_id = request.session_id
    user_id = request.user_id
    filename = request.dataset_name
    
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    redis_handler = RedisSessionHandler(session_id=session_id)
    logger.addHandler(redis_handler)
    
    logging.info(f"Searching for dataset with name: '{filename}'")
    if not request:
        raise HTTPException(status_code=400, detail="NO REQUEST")
            
    ### Each User has their own DB.
    ### Each DB has multiple collections.
    ### Each Collection is a dataset.
    ### A row in Collection is a data.  
    logging.debug(f"[{session_id}] Getting sesesion data from REDIS")
    stored_session_json = get_cache(session_id)
    
    if not stored_session_json:
        raise HTTPException(status_code=404, detail="Session not found or has expired.")
    logging.debug(f"[{session_id}] Loading sesesion data as JSON format")
    session_data = json.loads(stored_session_json)
    

    async with httpx.AsyncClient() as client:
        try:
            
            response = await client.get(f"http://{DB_HOST}:{DB_PORT}/v1/read/{filename}?user_id={user_id}")
            benchmark_dataset = response.json()
        except httpx.HTTPStatusError:
            logging.error(f" [api/v1/endpoints/dataset.py] {httpx.HTTPStatusError}")
    if benchmark_dataset is None:
        logging.error(f" [api/v1/endpoints/dataset.py] NO dataset found with name {filename}")
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with name '{filename}' not found.",
        )

    serialized_dataset = serialize_doc(benchmark_dataset)
    session_data["benchmark_dataset"] = serialized_dataset
    set_cache(session_id, session_data)

    return {"status": "OK"}

