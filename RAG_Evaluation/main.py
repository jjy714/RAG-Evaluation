from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from schema import EvaluationRequest, EvaluationStartResponse, EvaluationStatusResponse
from evaluator import evaluator
import uuid
import asyncio
import json
from api.v1.routers import api_router
# Import your graph creation function and state
from graphs.main_graph import create_main_graph, EvaluationState

app = FastAPI(
    title="RAG Evaluation API",
    description="An API to run RAG evaluation pipelines built with LangGraph.",
    version="1.0.0",
)
app.include_router(api_router, prefix="/api/v1")

# --- In-memory storage for evaluation status and results ---
evaluations = {}

# --- Background Task for Evaluation ---

async def run_evaluation(evaluation_id: str, request: EvaluationRequest):
    """
    Run an evaluation in the background.
    """
    evaluations[evaluation_id]["status"] = "running"
    print(f"--- Starting Evaluation {evaluation_id} ---")
    result = dict()
    try:
        # Create the main evaluation graph
        main_graph = create_main_graph()

        # The input for the graph must match the EvaluationState TypedDict
        initial_state: EvaluationState = {
            "evaluation_mode": request.evaluation_mode,
            "retrieve_metrics": request.retrieve_metrics,
            "generate_metrics": request.generate_metrics,
            "dataset": request.dataset.dict(),
            "retriever_evaluation_result": None,
            "generator_evaluation_result": None,
        }

        print(f"Invoking graph with mode: {request.evaluation_mode}")
        
        # Asynchronously invoke the graph with the state
        result["retriever_evaluation_result"], result["generator_evaluation_result"] = await evaluator(initial_state)
        print(f"--- Graph Execution Finished for {evaluation_id} ---")


        evaluations[evaluation_id]["status"] = "completed"
        evaluations[evaluation_id]["result"] = result

    except Exception as e:
        print(f"--- Evaluation {evaluation_id} Failed ---")
        print(e)
        evaluations[evaluation_id]["status"] = "failed"
        evaluations[evaluation_id]["result"] = {"error": str(e)}

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





async def dashboard_stream_generator():
    """
    A generator that yields SSE events for the dashboard.
    """
    while True:
        # In a real application, you would fetch the actual status
        # of the running evaluations and send updates.
        # For this example, we'll just send a ping.
        
        # Create a JSON object with the current status of all evaluations
        dashboard_data = {
            "evaluations": [
                {"id": eid, "status": evals["status"]}
                for eid, evals in evaluations.items()
            ]
        }
        
        yield f"data: {json.dumps(dashboard_data)}\n\n"
        await asyncio.sleep(1)

