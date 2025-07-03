from typing_extensions import TypedDict, List, Dict, Literal
from langgraph.graph import START, StateGraph, END
from datasets import Dataset

main_graph = []

"""
SUBGRAPH
class RetrieverEvaluationState(TypedDict):
    metrics: List[str]
    dataset: Dataset | List
    evaluation_result = Dict
"""



class EvaluationState(TypedDict):
    retrieve_metrics: List[str] | None
    generate_metrics: List[str] | None
    dataset: Dataset | List
    evaluation_mode: str
    retriever_evaluation_result = Dict
    generator_evaluation_result = Dict

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

def edit_graph():
    return

def router(state: EvaluationState):
    return

def evaluate_retrieval(state: EvaluationState):
    retriever_evaluation_result=[]
    return {"retriever_evaluation_result" : retriever_evaluation_result}

def evaluate_generation(state:EvaluationState):
    generator_evaluation_result=[] 
    return {"generator_evaluation_result" : generator_evaluation_result}


workflow = StateGraph(EvaluationState)

# Add the nodes to the graph
workflow.add_node("retrieval_evaluator", evaluate_retrieval)
workflow.add_node("generation_evaluator", evaluate_generation)

# Set the entry point
workflow.set_entry_point("router")

# Add the conditional router
workflow.add_conditional_edges(
    "router",
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