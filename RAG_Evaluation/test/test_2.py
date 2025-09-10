import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import Literal, List
from pydantic import BaseModel, ValidationError
from collections import defaultdict
import uuid

# --- Mock Dependencies ---
# In a real project, these would be imported from your actual source files.
# We define them here to make this test file runnable on its own.

SHARED_PROCESS = defaultdict(dict)

class RetrievalMetrics(BaseModel):
    precision: bool = False
    recall: bool = False

class GenerationMetrics(BaseModel):
    faithfulness: bool = False

class UserConfig(BaseModel):
    user_id: str
    retrieval_metrics: RetrievalMetrics
    generation_metrics: GenerationMetrics
    top_k: int
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"]

# --- The Endpoint Code to be Tested ---
# This is the code from your file (e.g., api/v1/endpoints/configuration.py)
from fastapi import APIRouter

router = APIRouter()

@router.post("/config")
async def store_config(config: UserConfig):
    """Stores the user's configuration and returns a new session ID."""
    session_id = str(uuid.uuid4())
    # Using defaultdict makes this assignment safe
    SHARED_PROCESS[session_id]["config"] = config
    return {"session_id": session_id, "message": "Session Configuration set successfully."}


# --- Test Application Setup ---
# Create a temporary FastAPI app instance just for testing.
app = FastAPI()
app.include_router(router)

# Create a single client instance to be reused across tests
client = TestClient(app)

# --- The Test Functions ---

def test_store_config_success():
    """
    Tests the /config endpoint for a successful request.
    It verifies the response and checks if the state was updated correctly.
    """
    # 1. Define the valid payload to send to the endpoint.
    test_config_payload = {
        "user_id": "user-123",
        "retrieval_metrics": {"precision": True},
        "generation_metrics": {"faithfulness": True},
        "top_k": 10,
        "evaluation_mode": "full"
    }

    # 2. Use TestClient to make a request to the test app.
    response = client.post("/config", json=test_config_payload)

    # 3. Assert the response is correct.
    assert response.status_code == 200
    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["message"] == "Session Configuration set successfully."

    # 4. Assert that the shared state was updated correctly.
    session_id = response_data["session_id"]
    assert session_id in SHARED_PROCESS
    
    stored_config = SHARED_PROCESS[session_id]["config"]
    assert isinstance(stored_config, UserConfig)
    assert stored_config.user_id == "user-123"
    assert stored_config.top_k == 10
    
    # Clean up the shared state after the test
    del SHARED_PROCESS[session_id]

def test_store_config_missing_required_field():
    """
    Tests that the endpoint returns a 422 Unprocessable Entity error
    if a required field (like 'user_id') is missing.
    """
    # Payload is missing the 'user_id' field.
    invalid_payload = {
        "retrieval_metrics": {"precision": True},
        "generation_metrics": {"faithfulness": True},
        "top_k": 10,
        "evaluation_mode": "full"
    }
    
    response = client.post("/config", json=invalid_payload)
    
    # FastAPI automatically returns a 422 error for Pydantic validation failures.
    assert response.status_code == 422
    response_data = response.json()
    assert "Field required" in str(response_data)
    assert "user_id" in str(response_data)

def test_store_config_invalid_data_type():
    """
    Tests that the endpoint returns a 422 error if a field has the wrong
    data type (e.g., 'top_k' as a string instead of an integer).
    """
    invalid_payload = {
        "user_id": "user-456",
        "retrieval_metrics": {"precision": True},
        "generation_metrics": {"faithfulness": True},
        "top_k": "ten",  # <-- Invalid type
        "evaluation_mode": "full"
    }
    
    response = client.post("/config", json=invalid_payload)
    
    assert response.status_code == 422
    response_data = response.json()
    assert "Input should be a valid integer" in str(response_data)

def test_store_config_invalid_enum_value():
    """
    Tests that the endpoint returns a 422 error if 'evaluation_mode'
    is not one of the allowed Literal values.
    """
    invalid_payload = {
        "user_id": "user-789",
        "retrieval_metrics": {},
        "generation_metrics": {},
        "top_k": 5,
        "evaluation_mode": "fast_mode"  # <-- Invalid enum value
    }
    
    response = client.post("/config", json=invalid_payload)
    
    assert response.status_code == 422
    response_data = response.json()
    assert "Input should be 'retrieval_only', 'generation_only' or 'full'" in str(response_data)

