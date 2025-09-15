import numpy as np
from typing import List, Dict, Union, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from metrics.Retrieval import RetrievalEvaluator
from time import sleep
from langchain_openai import AzureChatOpenAI, ChatOpenAI
import logging




"""
@TODO 

ADD A STEP BY STEP GRADUAL BATCHING ALGORITHM


"""




    
METRICS_LIST = ["mrr", "map", "f1", "ndcg", "context_relevance","precision", "recall" ]

# --- 2. Define the State for the Graph ---
# We add an 'evaluator' field to hold the instance and 'metrics_to_run_copy' for the router.
class RetrievalEvaluationState(TypedDict):
    # --- INPUTS ---
    query: List[str]
    predicted_documents: List[List[Document]]
    ground_truth_documents: List[List[Document]]
    metrics_to_run: List[str]
    model: AzureChatOpenAI | ChatOpenAI | str
    k: int
    # --- INTERNAL STATE ---
    evaluator: Optional[RetrievalEvaluator]

    # --- OUTPUT ---
    mrr_score: Optional[float]
    map_score: Optional[float]
    ndcg_score: Optional[float]
    context_relevance_score: Optional[float]
    
    precision_micro: Optional[float]
    precision_macro: Optional[float]
    recall_micro: Optional[float]
    recall_macro: Optional[float]
    f1_micro: Optional[float]
    f1_macro: Optional[float]

    final_results: Dict[str, float]

# --- 3. Define Separate Nodes for Each Task ---

def instantiate_evaluator_node(state: RetrievalEvaluationState) -> dict:
    """
    This is the first step. It creates the evaluator instance ONCE and
    initializes the results dictionary and metrics list copy.
    """
    print("\n--- (1) Instantiating Evaluator ---")
    evaluator = RetrievalEvaluator(
        query=state["query"],
        ground_truth_documents=state["ground_truth_documents"],
        predicted_documents=state["predicted_documents"],
        model=state["model"],
    )
    sleep(2)
    return {
        "evaluator": evaluator,
    }

def mrr_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the MRR score."""
    print("--- (2a) Running MRR Node ---")
    evaluator = state["evaluator"]
    k = state["k"]
    mrr_score = evaluator.mrr(k=k)
    sleep(2)
    return {
        "mrr_score": mrr_score
        }

def map_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the MAP score."""
    print("--- (2b) Running MAP Node ---")
    evaluator = state["evaluator"]
    k = state["k"]
    map_score = evaluator.map(k=k)
    sleep(2)
    return {"map_score": map_score}

def f1_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the f1 score."""
    print("--- (2c) Running f1 Node ---")
    evaluator = state["evaluator"]
    k = state["k"]
    f1_micro, f1_macro = evaluator.f1(k=k)
    # logging.DEBUG(f" F1 SCORE DEBUG: {f1_micro, f1_macro}")

    return {
        "f1_micro": f1_micro,
        "f1_macro": f1_macro
    }

def ndcg_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the NDCG score."""
    print("--- (2d) Running NDCG Node ---")
    evaluator = state["evaluator"]
    k = state["k"]
    ndcg_score = evaluator.ndcg(k=k)
    sleep(2)
    return {"ndcg_score": ndcg_score}

def context_relevance_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the Context Relevance score."""
    print("--- (2e) Running Context Relevance Node ---")
    evaluator = state["evaluator"]
    context_relevance_score = evaluator.context_relevance()
    sleep(2)
    return {"context_relevance_score": context_relevance_score}

def precision_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the Precision@5 score."""
    print("--- (2f) Running Precision Node ---")
    evaluator = state["evaluator"]
    k = state["k"]
    precision_micro, precision_macro = evaluator.precision(k=k)
    # logging.DEBUG(f" PRECISION SCORE DEBUG: {precision_micro, precision_macro}")
    sleep(2)
    return {
        "precision_micro": precision_micro,
        "precision_macro": precision_macro
    }

def recall_node(state: RetrievalEvaluationState) -> dict:
    """Node to calculate only the Recall@5 score."""
    print("--- (2g) Running Recall Node ---")
    evaluator = state["evaluator"]
    k = state["k"]    
    recall_micro, recall_macro = evaluator.recall(k=k)
    # logging.DEBUG(f" RECALL SCORE DEBUG: {recall_micro, recall_macro}")
    sleep(2)
    return {
        "recall_micro": recall_micro,
        "recall_macro": recall_macro
    }

def finalize_node(state: RetrievalEvaluationState) -> dict:
    """Optionally consolidate all scores into final_results."""
    print("--- (3) Finalizing Results ---")
    final_scores = {
        "mrr": state.get("mrr_score"),
        "map": state.get("map_score"),
        "ndcg": state.get("ndcg_score"),
        "context_relevance": state.get("context_relevance_score"),
        "f1_micro": state.get("f1_micro"),
        "f1_macro": state.get("f1_macro"),
        "precision_micro": state.get("precision_micro"),
        "precision_macro": state.get("precision_macro"),
        "recall_micro": state.get("recall_micro"),
        "recall_macro": state.get("recall_macro"),
    }
    # Remove any None entries
    final_scores = {k: v for k, v in final_scores.items() if v is not None}
    sleep(2)
    return {"final_results": final_scores}


def parallelize_metrics(state: RetrievalEvaluationState) -> str:
    print("--- Routing Metrics ---")
    
    metric = state["metrics_to_run"]
        
    if not state["metrics_to_run"]:
        print("→ All metrics computed. Go to finalize.")
        return "finalize"
    
    if metric not in METRICS_LIST:
        print("No evaluation metric selected\n Choose from the following metrics list \n{METRICS_LIST}")
    sleep(2)
    return metric
# --- 5. Build and Compile the Subgraph ---
def create_retrieval_subgraph(metrics_to_run: List[str]):
    workflow = StateGraph(RetrievalEvaluationState)
    METRIC_NODES = {
    "mrr": mrr_node,
    "map": map_node,
    "f1": f1_node,
    "ndcg": ndcg_node,
    "context_relevance": context_relevance_node,
    "precision": precision_node,
    "recall": recall_node
    }
    # Always present
    workflow.add_node("instantiate_evaluator", instantiate_evaluator_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("instantiate_evaluator")
    workflow.set_finish_point("finalize")

    for metric in metrics_to_run:
        if metric not in METRIC_NODES:
            raise ValueError(f"Unknown metric '{metric}'. Must be one of {list(METRIC_NODES.keys())}")

        node_name = f"{metric}_node"
        node_fn = METRIC_NODES[metric]
        # Add node
        workflow.add_node(node_name, node_fn)

        # Wire: instantiation → metric node
        workflow.add_edge("instantiate_evaluator", node_name)

        # Wire: metric node → finalize
        workflow.add_edge(node_name, "finalize")

    return workflow.compile()









