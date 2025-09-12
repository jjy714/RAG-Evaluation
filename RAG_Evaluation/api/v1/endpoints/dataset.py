from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from schema import BenchmarkRequest
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from cache_redis import get_cache, set_cache
from pathlib import Path 
import httpx
import json
import os

env_path = Path(".").parent.parent
load_dotenv(env_path)

## STEP 2. GET DATASET !!

DB_PORT= os.getenv("DB_PORT")
router = APIRouter()


def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

@router.post("/get-benchmark-dataset")
async def get_benchmark_dataset(request: BenchmarkRequest):
    print(f"Searching for dataset with name: '{request.dataset_name}'")
    if not request:
        raise HTTPException(status_code=400, detail="NO REQUEST")
            
    ### Each User has their own DB.
    ### Each DB has multiple collections.
    ### Each Collection is a dataset.
    ### A row in Collection is a data.  
    stored_session_json = get_cache(request.session_id)
    if not stored_session_json:
        raise HTTPException(status_code=404, detail="Session not found or has expired.")
    session_data = json.loads(stored_session_json)
    
    user_id = request.user_id
    session_id = request.session_id
    filename = request.dataset_name
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:{DB_PORT}/v1/read/{filename}?user_id={user_id}")
        benchmark_dataset = response.json()
        
    if benchmark_dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with name '{request.dataset_name}' not found.",
        )

    serialized_dataset = serialize_doc(benchmark_dataset)
    session_data["benchmark_dataset"] = serialized_dataset
    set_cache(session_id, session_data)

    return {"status": "OK"}

