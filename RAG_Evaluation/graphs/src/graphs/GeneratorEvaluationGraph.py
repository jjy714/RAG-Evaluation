from langgraph.graph import StateGraph
from typing_extensions import TypedDict, List, Dict, Optional
from datasets import Dataset
from metrics.Generation import GenerationEvaluator
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from time import sleep
from core import RedisSessionHandler
import numpy as np
import logging



            # query: List[str],
            # ground_truth_answer: List[List[Document]],
            # retrieved_contexts: List[List[Document]],
            # generated_answer: List[str],
            # model: str
            # ):

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

METRICS_LIST=['rouge', 'bleu', 'faithfulness']

class GeneratorEvaluationState(TypedDict):
    query: Dataset | List 
    ground_truth_answer: List
    retrieved_contexts: List
    generated_answer: List
    model: ChatOpenAI | AzureChatOpenAI | str
    
    evaluator: Optional[GenerationEvaluator]

    rouge_score: Optional[float]
    bleu_score: Optional[float]
    faithfulness_score: Optional[float]
    final_results: Dict[str, float]


def instantiate_evaluator_node(state: GeneratorEvaluationState) -> dict:
    """
    This is the first step. It creates the evaluator instance ONCE and
    initializes the results dictionary and metrics list copy.
    """
    redis_handler = RedisSessionHandler(session_id=state["session_id"])
    logger.addHandler(redis_handler)
    
    logger.info("\n--- (1) Instantiating Evaluator ---")
    evaluator = GenerationEvaluator(
        query=state["query"],
        ground_truth_answer=state["ground_truth_answer"],
        retrieved_contexts=state["retrieved_contexts"],
        generated_answer=state["generated_answer"],
        model=state["model"],
    )
    sleep(2)
    return {
        "evaluator": evaluator,
    }

async def rouge_node(state: GeneratorEvaluationState):
    """Node to calculate only the ROUGE score."""
    logger.info("--- (2a) Running rouge Node ---")
    evaluator = state["evaluator"]
    rouge_score = await evaluator.rouge()
    sleep(2)
    return {"rouge_score": rouge_score}

async def bleu_node(state: GeneratorEvaluationState):
    """Node to calculate only the BLEU score."""
    logger.info("--- (2b) Running BLEU Node ---")
    evaluator = state["evaluator"]
    bleu_score = await evaluator.bleu()
    sleep(2)
    return {"bleu_score": bleu_score}


async def faithfulness_node(state: GeneratorEvaluationState):
    """Node to calculate only the Faithfulness score."""
    logger.info("--- (2c) Running Faithfulness Node ---")
    evaluator = state["evaluator"]
    faithfulness_score = await evaluator.faithfulness()
    sleep(2)
    return {"faithfulness_score": faithfulness_score}

def finalize_node(state: GeneratorEvaluationState) -> dict:
    """Optionally consolidate all scores into final_results."""
    logger.info("--- (3) Finalizing Results ---")
    final_scores = {
        "rouge": state.get("rouge_score"),
        "bleu": state.get("bleu_score"),
        "faithfulness": state.get("faithfulness_score"),
    }
    # Remove any None entries
    final_scores = {k: v for k, v in final_scores.items() if v is not None}
    sleep(2)
    return {"final_results": final_scores}



def parallelize_metrics(state: GeneratorEvaluationState) -> str:
    logger.info("--- Routing Metrics ---")
    
    metric = state["metrics_to_run"]
        
    if not state["metrics_to_run"]:
        logger.info("→ All metrics computed. Go to finalize.")
        return "finalize"
    
    if metric not in METRICS_LIST:
        logger.info("No evaluation metric selected\n Choose from the following metrics list \n{METRICS_LIST}")
    sleep(2)
    return metric
# --- 5. Build and Compile the Subgraph ---
def create_generation_subgraph(metrics_to_run: List[str]):
    workflow = StateGraph(GeneratorEvaluationState)
    METRIC_NODES = {
    "rouge": rouge_node,
    "bleu": bleu_node,
    "faithfulness": faithfulness_node,
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



