from typing_extensions import TypedDict, List, Dict
from langgraph.graph import START, StateGraph, END
from datasets import Dataset

main_graph = []

class EvaluationState(TypedDict):
    metrics: List[Dict[str]]
    dataset: Dataset | List
    evaluation_result = Dict[int|float]

def route_evaluations(state: EvaluationState) -> Literal["retrieval_evaluator", "generation_evaluator"]:
    """
    Router function to direct the graph based on the evaluation_mode.
    """
    print("--- (*) Routing... ---")
    mode = state["evaluation_mode"]
    
    if mode == "retrieval_only":
        print("Decision: Route to Retrieval Evaluator ONLY.")
        return "retrieval_evaluator"
    elif mode == "generation_only":
        print("Decision: Route to Generation Evaluator ONLY.")
        return "generation_evaluator"
    elif mode == "full":
        print("Decision: Route to Retrieval, then Generation.")
        return "retrieval_evaluator"
    else:
        raise ValueError(f"Invalid evaluation_mode: {mode}")



workflow = StateGraph(EvaluationState)

# Add the nodes to the graph
workflow.add_node("rag_pipeline", run_rag_pipeline)
workflow.add_node("retrieval_evaluator", evaluate_retrieval)
workflow.add_node("generation_evaluator", evaluate_generation)

# Set the entry point
workflow.set_entry_point("rag_pipeline")

# Add the conditional router
workflow.add_conditional_edges(
    "rag_pipeline",
    route_evaluations,
    {
        "retrieval_evaluator": "retrieval_evaluator",
        "generation_evaluator": "generation_evaluator",
    },
)

# Define the sequential path for "full" evaluation
workflow.add_edge("retrieval_evaluator", "generation_evaluator")

# Define the end points for the graph
workflow.add_edge("generation_evaluator", END)


# Compile the graph into a runnable application
graph = workflow.compile()