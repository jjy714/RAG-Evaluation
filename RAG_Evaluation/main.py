from fastapi import FastAPI
from api.v1.endpoints.evaluator import evaluator
from api.v1.routers import api_router
from graphs.main_graph import create_main_graph, EvaluationState
from core.post_data import DataPointApiClient
from typing import Any, Dict

app = FastAPI(
    title="RAG Evaluation API",
    description="An API to run RAG evaluation pipelines built with LangGraph.",
    version="1.0.0",
)
app.include_router(api_router, prefix="/v1")

# @TODO
"""
1. Create Logging sequence
Log as a file and store in User's -> session -> table in DB

2. Make the graph interaction individual to interact with the frontend. 

"""

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok"}

###### 
@app.post("/send-datapoint")
async def main(session_id: str, endpoint: str, payload: Dict[str, Any]):
    sender = DataPointApiClient(session_id, endpoint)
    return await sender.send_datapoint(payload)


@app.post("/eval_result") # 
async def get_eval_result(payload: Dict[str, Any]):
    print("payload:", payload)
    return {"eval_result": payload}