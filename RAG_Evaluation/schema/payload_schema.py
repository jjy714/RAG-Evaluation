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

# api/v1/configuration
class RetrievalMetrics(BaseModel):
    retrieval_metrics: List[str]

# api/v1/configuration
class GenerationMetrics(BaseModel):
    generation_metrics: List[str]

# api/v1/configuration
class UserConfig(BaseModel):
    user_id: str
    retrieval_metrics: RetrievalMetrics
    generation_metrics: GenerationMetrics
    top_k: int 
    evaluation_mode: str

# api/v1/dataset
class BenchmarkRequest(BaseModel):
    session_id: str
    dataset_name: str