from metrics import GenerationEvaluator, RetrievalEvaluator

from langgraph.graph import START, StateGraph, END
from langchain_core.documents import Document
from typing_extensions import TypedDict, List, Dict
from datasets import Dataset, load_dataset, load_from_disk

graph=[]






def create_graph(selected_metrices):
    graph_builder = StateGraph(EvaluationState).add_sequence(selected_metrices)
    for idx in range(len(selected_metrices)):
        if idx == 0:
            graph_builder.add_edge(START, selected_metrices[idx+1])
        if idx + 1 == len(selected_metrices):
            graph_builder.add_edge(selected_metrices[idx], END)
            break
        else:
            graph_builder.add_edge(selected_metrices[idx], selected_metrices[idx+1])
    graph_builder.add_edge("generate", END)
    graph = graph_builder.compile()

create_graph()
def run_graph():
    response = graph.invoke({"metrics": metrics, "dataset": dataset, "evaluation_result": []})
