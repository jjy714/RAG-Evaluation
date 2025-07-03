
from typing_extensions import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from datasets import Dataset
from metrics import RetrievalEvaluator



class RetrieverEvaluationState(TypedDict):
    metrics: List[str]
    dataset: Dataset | List
    evaluation_result = Dict

_retriever = RetrievalEvaluator()

def get_metrics(state:RetrieverEvaluationState):
    return state["metrics"]

def get_dataset(state: RetrieverEvaluationState):
    return state["dataset"]

metrics_list = get_metrics(RetrieverEvaluationState)
dataset = get_dataset(RetrieverEvaluationState)

def precision_node(state:RetrieverEvaluationState):
    result = _retriever.precision()
    return {"evaluation_result" : result}

def recall_node():
    result = _retriever.recall()
    return result

def mrr_node():
    result = _retriever.mrr()
    return result

def map_node():
    result = _retriever.map()
    return result

def accuracy_node():
    result = _retriever.accuracy()
    return result

def faithfulness_node():
    result = _retriever.faithfulness()
    return result

def noise_sensitivity_node():
    result = _retriever.noise_sensitivity_node()
    return result

def response_relevancy_node():
    result = _retriever.response_relevancy_node()
    return result

def init_graph():
    workflow = StateGraph(RetrieverEvaluationState)
    for idx in range(len(get_metrics(RetrieverEvaluationState))):
        workflow.add_node(metrics_list[idx], metrics_list[idx+1])
    RetrievalSubGraph = workflow.compile()
    return RetrievalSubGraph