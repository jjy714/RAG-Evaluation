from langchain_core.documents import Document
from krag.document import Document as KrDocument
from typing import List, Dict, Optional
from datasets import Dataset

def datatype_checker(main_graph_data, retrieval_graph_data, generator_graph_data):
    
    # **kwargs -> parameter_name = value -->> {"parameter_name" : value}
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
    if not isinstance(data, List):
        assert()
    if not isinstance(data, Dict):
        assert()
    if not isinstance(data, Optional):
        assert()
    if not isinstance(data, Dataset):
        assert()
    if not isinstance(data, Document):
        assert()
    if not isinstance(data, KrDocument):
        assert()

    return 