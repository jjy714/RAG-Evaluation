from fastapi import FastAPI
from api.v1.endpoints.evaluator import evaluator
from api.v1.routers import api_router
from graphs.main_graph import create_main_graph, EvaluationState

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

