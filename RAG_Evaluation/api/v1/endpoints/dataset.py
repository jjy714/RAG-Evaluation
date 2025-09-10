from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from schema import BenchmarkRequest
from dotenv import load_dotenv
from SHARED_PROCESS import SHARED_PROCESS


router = APIRouter()


def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.post("/get-benchmark-dataset")
def get_benchmark_dataset(request: BenchmarkRequest):
    print(f"Searching for dataset with name: '{request.dataset_name}'")

    if request.session_id not in SHARED_PROCESS:
        assert not request.session_id
        return HTTPException(
            status_code=400, detail=f"Session ID {request.session_id} is invalid"
        )
    client = MongoClient("mongodb://root:example_password@mongodb:27017/")
    user_id = SHARED_PROCESS[request.session_id]["user_id"] + "_DB"
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
