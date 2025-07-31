from pydantic import BaseModel
from typing import List, Optional, Literal, Dict
from langchain_core.documents import Document
from fastapi import File
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
    user_id: int
    session_id: int
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
