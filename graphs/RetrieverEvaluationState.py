
from typing_extensions import TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from datasets import Dataset
from metrics import RetrievalEvaluator

_retriever = RetrievalEvaluator()

class RetrieverEvaluationState(TypedDict):
    dataset: Dataset | List
    evaluation_result = Dict



def precision(state:RetrieverEvaluationState):
    result = _retriever.precision()
    return {"evaluation_result" : result}





workflow = StateGraph(RetrieverEvaluationState)
workflow.add_node()