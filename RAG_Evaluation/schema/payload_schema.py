from pydantic import BaseModel
from typing import List, Optional, Literal, Dict
from langchain_core.documents import Document
from fastapi import File
# --- Pydantic Models for API Data Structure ---
"""
  Args: 
    **kwargs : main_graph_data, retrieval_graph_data, generator_graph_data 
        MAIN GRAPH:
        class EvaluationState(TypedDict):
            retrieve_metrics: List[str] | None
            generate_metrics: List[str] | None
            dataset: Dataset | List
            evaluation_mode: str
            retriever_evaluation_result = Dict
            generator_evaluation_result = Dict

    RETRIEVAL SUBGRAPH:
        class RetrievalEvaluationState(TypedDict):
            # --- INPUTS ---
            predicted_documents: List[List[Document]]
            actual_documents: List[List[Document]]
            metrics_to_run: List[str]
            k: int

            # --- INTERNAL STATE ---
            evaluator: Optional[RetrievalEvaluator]

            # --- OUTPUT ---
            mrr_score: Optional[float]
            precision_score: Optional[float]
            recall_score: Optional[float]
            f1_score: Optional[float]
            ndcg_score: Optional[float]
            final_results: Dict[str, float]

            
        GENERATION SUBGRAPH:
        class GeneratorEvaluationState(TypedDict):
            user_input: Dataset | List 
            reference: List
            retrieved_contexts: List
            response: List
            model: ChatOpenAI | AzureChatOpenAI | str
            
            evaluator: Optional[GenerationEvaluator]

            rouge_score: Optional[float]
            bleu_score: Optional[float]
            faithfulness_score: Optional[float]
            final_results: Dict[str, float]
    
"""


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
