from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from schema import BenchmarkRequest
from dotenv import load_dotenv
from SHARED_PROCESS import SHARED_PROCESS





router = APIRouter()

# --- Pydantic model for the request body ---
# This ensures the incoming JSON has the correct structure.


# Helper function to convert MongoDB's ObjectId to a string
def serialize_doc(doc):
    # Make it more robust: only convert _id if it exists
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# --- Corrected FastAPI Endpoint ---
# Use a more descriptive name and path
@router.post("/get-benchmark-dataset")
def get_benchmark_dataset(request: BenchmarkRequest):
    """
    Retrieves a specific benchmark dataset from the MongoDB collection by its name.
    """
    print(f"Searching for dataset with name: '{request.dataset_name}'")
    
    if request.session_id not in SHARED_PROCESS:
        assert not request.session_id
        return HTTPException(
            status_code=400,
            detail=f"Session ID {request.session_id} is invalid"
            )
    client = MongoClient("mongodb://root:example_password@mongodb:27017/")
    user_id = SHARED_PROCESS[request.session_id]["user_id"] + "_DB"
    db = client.user_id
    collection = db.benchmark_datasets

    benchmark_dataset = collection.find({"file_name": request.dataset_name})
    
    # 2. THE FIX: Add error handling for when the dataset is not found
    if benchmark_dataset is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Dataset with name '{request.dataset_name}' not found."
        )
    
    # 3. Serialize the single document before returning
    serialized_dataset = serialize_doc(benchmark_dataset)
    
    SHARED_PROCESS[request.session_id]["benchmark_dataset"] = serialized_dataset
    
    # 4. THE FIX: Return the correct, serialized variable
    return {"status" : "OK"}