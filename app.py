from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Literal, Optional
import uuid
import asyncio
import json

# Import your graph creation function and state
from graphs.main_graph import create_main_graph, EvaluationState

app = FastAPI(
    title="RAG Evaluation API",
    description="An API to run RAG evaluation pipelines built with LangGraph.",
    version="1.0.0",
)

# --- In-memory storage for evaluation status and results ---
evaluations = {}

# --- Pydantic Models for API Data Structure ---

# Define the structure for the data needed for retrieval evaluation
class RetrievalData(BaseModel):
    predicted_documents: List[List[str]]
    actual_documents: List[List[str]]
    k: int


# Define the structure for the data needed for generation evaluation
class GenerationData(BaseModel):
    query: List[str]
    reference: List[str]
    retrieved_contexts: List[List[str]]
    response: List[str]
    model: str


# Combine the data structures into a single dataset model
class EvaluationDataset(BaseModel):
    Retrieval: Optional[RetrievalData] = None
    Generation: Optional[GenerationData] = None


# The main request body for the /evaluate endpoint
class EvaluationRequest(BaseModel):
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"]
    retrieve_metrics: Optional[List[str]] = None
    generate_metrics: Optional[List[str]] = None
    dataset: EvaluationDataset


# The response model for starting an evaluation
class EvaluationStartResponse(BaseModel):
    evaluation_id: str

# The response model for checking evaluation status
class EvaluationStatusResponse(BaseModel):
    status: str
    result: Optional[Dict] = None

# --- Background Task for Evaluation ---

async def run_evaluation(evaluation_id: str, request: EvaluationRequest):
    """
    Run an evaluation in the background.
    """
    evaluations[evaluation_id]["status"] = "running"
    print(f"--- Starting Evaluation {evaluation_id} ---")

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
        final_state = await main_graph.ainvoke(initial_state)
        
        print(f"--- Graph Execution Finished for {evaluation_id} ---")

        # Extract the relevant results from the final state
        result = {
            "retriever_evaluation": final_state.get("retriever_evaluation_result"),
            "generator_evaluation": final_state.get("generator_evaluation_result"),
        }

        evaluations[evaluation_id]["status"] = "completed"
        evaluations[evaluation_id]["result"] = result

    except Exception as e:
        print(f"--- Evaluation {evaluation_id} Failed ---")
        print(e)
        evaluations[evaluation_id]["status"] = "failed"
        evaluations[evaluation_id]["result"] = {"error": str(e)}


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/evaluations", response_model=EvaluationStartResponse, status_code=202)
async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    Starts a new evaluation as a background task.
    """
    evaluation_id = str(uuid.uuid4())
    evaluations[evaluation_id] = {"status": "pending", "result": None}
    background_tasks.add_task(run_evaluation, evaluation_id, request)
    return {"evaluation_id": evaluation_id}

@app.get("/evaluations/{evaluation_id}", response_model=EvaluationStatusResponse)
def get_evaluation_status(evaluation_id: str):
    """
    Checks the status and results of an evaluation.
    """
    evaluation = evaluations.get(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation

@app.get("/system/info")
def get_system_info():
    """
    Retrieves metadata and graph information.
    """
    # This is a placeholder. In a real application, you would
    # dynamically get this information.
    return {
        "graph": "MainEvaluationGraph",
        "parameters": {
            "supported_modes": ["retrieval_only", "generation_only", "full"],
            "supported_retrieval_metrics": ["accuracy", "precision", "recall", "map", "mrr"],
            "supported_generation_metrics": ["bertscore", "bleu", "rouge", "faithfulness", "g-eval"]
        }
    }

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

@app.get("/dashboard/stream")
async def dashboard_stream(request: Request):
    """
    Streams live updates from the dashboard using SSE.
    """
    return StreamingResponse(dashboard_stream_generator(), media_type="text/event-stream")
