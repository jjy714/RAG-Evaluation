from typing import List, Dict, Literal, Union, Optional
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from datasets import Dataset
from .RetrieverEvaluationGraph import create_retrieval_subgraph, RetrievalEvaluationState
from .GeneratorEvaluationGraph import create_generation_subgraph, GeneratorEvaluationState
from core import RedisSessionHandler
import logging
import asyncio
    

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# --- EvaluationState Type ---
class EvaluationState(TypedDict):
    retrieve_metrics: Optional[List[str]]
    generate_metrics: Optional[List[str]]
    dataset: Union[Dataset, List]
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"]
    retriever_evaluation_result: Optional[Dict]
    generator_evaluation_result: Optional[Dict]
    session_id: str
    

# --- Router Function ---
def route_evaluations(state: EvaluationState) -> Literal["retrieval_evaluator", "generation_evaluator"]:
    redis_handler = RedisSessionHandler(session_id=state["session_id"])
    logger.addHandler(redis_handler)
        
    logging.info("--- (*) Routing Evaluation Mode ---")
    mode = state["evaluation_mode"]
    if "retrieval_only" in mode:
        logging.info("→ Route to Retrieval Evaluator ONLY")
        return "retrieval_evaluator"
    elif "generation_only" in mode:
        logging.info("→ Route to Generation Evaluator ONLY")
        return "generation_evaluator"
    elif "full" in mode:
        logging.info("→ Route to Retrieval THEN Generation")
        return "full"
    else:
        raise ValueError(f"Invalid evaluation_mode: {mode}")


# --- Retrieval Evaluation Wrapper ---
async def evaluate_retrieval(state: EvaluationState) -> Dict:
    retrieve_subgraph = create_retrieval_subgraph(state["retrieve_metrics"])

    retrieval_input: RetrievalEvaluationState = {
        "query":  Optional[state["dataset"]["Retrieval"]["query"]],
        "predicted_documents": state["dataset"]["Retrieval"]["predicted_documents"],
        "ground_truth_documents": state["dataset"]["Retrieval"]["ground_truth_documents"],
        "metrics_to_run": state["retrieve_metrics"],
        "model": state["dataset"]["Generation"]["model"],
        "k": state["dataset"]["Retrieval"]["k"],
        "session_id": state["session_id"],
    }

    results = await retrieve_subgraph.ainvoke(retrieval_input)
    results = results.get('final_results')
    return {"retriever_evaluation_result": results}


# --- Generation Evaluation Stub ---
async def evaluate_generation(state: EvaluationState) -> Dict:
    
    generate_subgraph = create_generation_subgraph(state["generate_metrics"])
    # print(f"[MAIN GRAPH] state['dataset']['Generation']['retrieved_contexts'] : {state['dataset']['Generation']['retrieved_contexts']}")
    generation_input: GeneratorEvaluationState = {
        "query": state["dataset"]["Generation"]["query"], 
        "ground_truth_answer": state["dataset"]["Generation"]["ground_truth_answer"], 
        "retrieved_contexts": state["dataset"]["Generation"]["retrieved_contexts"],
        "generated_answer": state["dataset"]["Generation"]["generated_answer"],
        "metrics_to_run": state["generate_metrics"],
        "model": state["dataset"]["Generation"]["model"]
    }
    results = await generate_subgraph.ainvoke(generation_input)
    results = results.get('final_results')
    return {"generator_evaluation_result": results}


# --- Router Node Definition ---
def router(state: EvaluationState) -> Dict:
    
    return {}  # No update needed, just branching


# --- Create Main Graph ---
def create_main_graph():
    workflow = StateGraph(EvaluationState)

    # Nodes
    workflow.add_node("router", router)
    workflow.add_node("retrieval_evaluator", evaluate_retrieval)
    workflow.add_node("generation_evaluator", evaluate_generation)

    # Entry point
    workflow.set_entry_point("router")
    # Routing logic
    workflow.add_conditional_edges(
        "router",
        route_evaluations,
        {
            "retrieval_evaluator": "retrieval_evaluator",
            "generation_evaluator": "generation_evaluator",
            "full": "retrieval_evaluator",
        },
    )
    workflow.add_conditional_edges(
        "retrieval_evaluator",
        route_evaluations,
        {
            "retrieval_evaluator": END,
            "full" : "generation_evaluator",
        },
    )
    # Endpoints
    workflow.add_edge("generation_evaluator", END)


    return workflow.compile()