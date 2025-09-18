from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
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


# api/v1/configuration
class RetrievalMetrics(BaseModel):
    retrieval_metrics: List[Literal["mrr", "map", "f1", "ndcg", "precision", "recall"]]


# api/v1/configuration
class GenerationMetrics(BaseModel):
    generation_metrics: List[Literal["bleu", "rouge", "faithfulness"]]


# api/v1/configuration
class UserConfig(BaseModel):
    user_id: str
    retrieve_metrics: List[Literal["mrr", "map", "f1", "ndcg", "precision", "recall"]]
    generate_metrics: List[Literal["bleu", "rouge", "faithfulness"]]
    top_k: int = 5
    model: Optional[str | None]
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"]


# api/v1/dataset
class BenchmarkRequest(BaseModel):
    session_id: str
    user_id: str
    dataset_name: str


# api/v1/evaluator
class EvaluationRequest(BaseModel):
    session_id: str
    user_id: str


class RetrievalModel(BaseModel):
    query: List[str] = Field(..., description="The input query or question.")
    predicted_documents: List[Document] = Field(
        ..., description="List of predicted document IDs."
    )
    ground_truth_documents: List[List[Document]] = Field(
        ..., description="List of ground truth document IDs."
    )
    model: str = Field(
        ...,
        description="Identifier for the model used for generation (e.g., 'azure', 'openai').",
    )
    k: int = Field(
        ..., description="The number of top documents considered for retrieval metrics."
    )


class GenerationModel(BaseModel):
    query: List[str] = Field(..., description="The input query or question.")
    ground_truth_answer: List[List[Document | str]] = Field(
        ..., description="The ground truth or reference answer."
    )
    retrieved_contexts: List[List[Document | str]] = Field(
        ..., description="The list of context strings passed to the generator."
    )
    generated_answer: List[str] = Field(
        ..., description="The generated response from the RAG model."
    )
    model: str | None = Field(
        description="Identifier for the model used for generation (e.g., 'azure', 'openai')."
    )


class DatasetModel(BaseModel):
    Retrieval: RetrievalModel
    Generation: GenerationModel


class GraphSchema(BaseModel):
    retrieve_metrics: RetrievalMetrics = Field(
        ..., description="A list of retrieval metrics to be calculated."
    )
    generate_metrics: GenerationMetrics = Field(
        ..., description="A list of generation metrics to be calculated."
    )
    dataset: DatasetModel = Field(
        ..., description="The dataset containing retrieval and generation data."
    )
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"] = Field(
        ..., description="The evaluation mode to run."
    )


# core/post_data
class DataPoint(BaseModel):
    session_id: str
    endpoint: str
    payload: Dict[str, Any]  
