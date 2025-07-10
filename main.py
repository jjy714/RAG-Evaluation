from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Literal, Optional

# Import your graph creation function and state
from graphs.main_graph import create_main_graph, EvaluationState

app = FastAPI(
    title="RAG Evaluation API",
    description="An API to run RAG evaluation pipelines built with LangGraph.",
    version="1.0.0",
)


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


# The response model
class EvaluationResponse(BaseModel):
    result: Dict


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Evaluation API"}


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluationRequest):
    """
    Run an evaluation based on the provided mode, metrics, and dataset.
    """
    print("--- Received Evaluation Request ---")
    
    # Create the main evaluation graph
    main_graph = create_main_graph()

    # The input for the graph must match the EvaluationState TypedDict
    # We construct it from our Pydantic model
    initial_state: EvaluationState = {
        "evaluation_mode": request.evaluation_mode,
        "retrieve_metrics": request.retrieve_metrics,
        "generate_metrics": request.generate_metrics,
        # Pydantic .dict() method converts the model to a dictionary
        "dataset": request.dataset.dict(),
        "retriever_evaluation_result": None,
        "generator_evaluation_result": None,
    }

    print(f"Invoking graph with mode: {request.evaluation_mode}")
    
    # Asynchronously invoke the graph with the state
    final_state = await main_graph.ainvoke(initial_state)
    
    print("--- Graph Execution Finished ---")

    # Extract the relevant results from the final state
    result = {
        "retriever_evaluation": final_state.get("retriever_evaluation_result"),
        "generator_evaluation": final_state.get("generator_evaluation_result"),
    }

    return EvaluationResponse(result=result)