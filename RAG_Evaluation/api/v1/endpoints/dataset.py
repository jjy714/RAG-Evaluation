from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from schema import BenchmarkRequest
from dotenv import load_dotenv
from typing import List
from langchain_core.documents import Document
from ..SHARED_PROCESS import SHARED_PROCESS
from pathlib import Path 
import os

env_path = Path(".").parent.parent
load_dotenv(env_path)

## STEP 2. GET DATASET !!

MONGO_PORT= os.getenv("MONGO_PORT")
MONGO_URI = f"mongodb://localhost:{MONGO_PORT}/"
MONGO_DB_NAME= os.getenv("MONGO_DB_NAME")
MONGO_INITDB_ROOT_USERNAME= os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD= os.getenv("MONGO_INITDB_ROOT_PASSWORD")
ME_CONFIG_MONGODB_URL= os.getenv("ME_CONFIG_MONGODB_URL")


router = APIRouter()


def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc



@router.post("/get-benchmark-dataset")
def get_benchmark_dataset(request: BenchmarkRequest):
    print(f"Searching for dataset with name: '{request.dataset_name}'")

    if request.session_id != SHARED_PROCESS["session_id"]:
        assert not request.session_id
        raise HTTPException(
            status_code=400, detail=f"Session ID {request.session_id} is invalid"
        )
    try:
        client = MongoClient(MONGO_URI, username=MONGO_INITDB_ROOT_USERNAME, password=MONGO_INITDB_ROOT_PASSWORD)
    except ConnectionError as CE:
        raise CE
            
    
    ### Each User has their own DB.
    ### Each DB has multiple collections.
    ### Each Collection is a dataset.
    ### A row in Collection is a data.  
    
    
    user_id = SHARED_PROCESS[request.session_id]["config"]["user_id"] + "_DB"
    db = client.user_id
    collection = db.benchmark_datasets

    benchmark_dataset = collection.find({"file_name": request.dataset_name})

    if benchmark_dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with name '{request.dataset_name}' not found.",
        )

    serialized_dataset = serialize_doc(benchmark_dataset)
    SHARED_PROCESS[request.session_id]["benchmark_dataset"] = serialized_dataset

    return {"status": "OK"}
