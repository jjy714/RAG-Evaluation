from fastapi import APIRouter

router = APIRouter()




@router.get("/systems/info")
def get_system_info():
    """
    Retrieves metadata and graph information.
    """
    # This is a placeholder. In a real application, you would
    # dynamically get this information.
    return {
        "graph": "MainEvaluationGraph",
        "parameters": {
            "supported_modes": ["retrieval_only", "generation_only", "full"],
            "supported_retrieval_metrics": ["accuracy", "precision", "recall", "map", "mrr"],
            "supported_generation_metrics": ["bertscore", "bleu", "rouge", "faithfulness", "g-eval"]
        }
    }
