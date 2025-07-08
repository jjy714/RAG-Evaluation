from typing import List, Dict, Literal, Union, Optional
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph
from datasets import Dataset
from .RetrieverEvaluationGraph import create_retrieval_subgraph, RetrievalEvaluationState
from .GeneratorEvaluationGraph import create_generation_subgraph, GeneratorEvaluationState

# --- EvaluationState Type ---
class EvaluationState(TypedDict):
    retrieve_metrics: Optional[List[str]]
    generate_metrics: Optional[List[str]]
    dataset: Union[Dataset, List]
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"]
    retriever_evaluation_result: Optional[Dict]
    generator_evaluation_result: Optional[Dict]


# --- Router Function ---
def route_evaluations(state: EvaluationState) -> Literal["retrieval_evaluator", "generation_evaluator"]:
    print("--- (*) Routing Evaluation Mode ---")
    mode = state["evaluation_mode"]

    if "retrieval_only" in mode:
        print("→ Route to Retrieval Evaluator ONLY")
        return "retrieval_evaluator"
    elif "generation_only" in mode:
        print("→ Route to Generation Evaluator ONLY")
        return "generation_evaluator"
    elif "full" in mode:
        print("→ Route to Retrieval THEN Generation")
        return "retrieval_evaluator"
    else:
        raise ValueError(f"Invalid evaluation_mode: {mode}")


# --- Retrieval Evaluation Wrapper ---
def evaluate_retrieval(state: EvaluationState) -> Dict:
    retrieve_subgraph = create_retrieval_subgraph(state["retrieve_metrics"])

    retrieval_input: RetrievalEvaluationState = {
        "predicted_documents": state["dataset"]["Retrieval"]["predicted_documents"],
        "actual_documents": state["dataset"]["Retrieval"]["actual_documents"],
        "metrics_to_run": state["retrieve_metrics"],
        "k": state["dataset"]["Retrieval"]["k"],
    }

    results = retrieve_subgraph.invoke(retrieval_input)
    results = results.get('final_results')
    return {"retriever_evaluation_result": results}


# --- Generation Evaluation Stub ---
def evaluate_generation(state: EvaluationState) -> Dict:
    
    generate_subgraph = create_generation_subgraph(state["generate_metrics"])

    generation_input: GeneratorEvaluationState = {
        "user_input": state["dataset"]["Generation"]["query"], 
        "reference": state["dataset"]["Generation"]["reference"], 
        "retrieved_contexts": state["dataset"]["Generation"]["retrieved_contexts"],
        "response": state["dataset"]["Generation"]["response"],
        "metrics_to_run": state["generate_metrics"],
        "model": state["dataset"]["Generation"]["model"]
    }
    results = generate_subgraph.invoke(generation_input)
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
        },
    )

    # Sequential path for "full" evaluation
    workflow.add_edge("retrieval_evaluator", "generation_evaluator")

    # Endpoints
    workflow.add_edge("generation_evaluator", END)
    workflow.add_edge("retrieval_evaluator", END)  # For "retrieval_only"

    return workflow.compile()