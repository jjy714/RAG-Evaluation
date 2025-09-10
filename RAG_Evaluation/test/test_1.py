import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient  # <-- 1. Import TestClient
from typing import Literal, List
from pydantic import BaseModel
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


# --- The Test Function (Now Synchronous) ---
def test_store_config_success():  # <-- 2. Removed 'async'
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
    client = TestClient(app)  # <-- 3. Instantiate TestClient
    response = client.post("/config", json=test_config_payload) # <-- 4. Make a synchronous call

    # 3. Assert the response is correct.
    assert response.status_code == 200
    response_data = response.json()
    assert "session_id" in response_data
    assert response_data["message"] == "Session Configuration set successfully."

    # 4. Assert that the shared state was updated correctly.
    session_id = response_data["session_id"]
    assert session_id in SHARED_PROCESS
    
    # Verify that the stored config object matches the payload we sent.
    stored_config = SHARED_PROCESS[session_id]["config"]
    assert isinstance(stored_config, UserConfig)
    assert stored_config.user_id == "user-123"
    assert stored_config.top_k == 10
    assert stored_config.retrieval_metrics.precision is True
    assert stored_config.generation_metrics.faithfulness is True
    
    # Clean up the shared state after the test
    del SHARED_PROCESS[session_id]

