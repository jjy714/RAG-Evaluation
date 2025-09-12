from typing import List
from schema import EvaluationRequest, GraphSchema, RetrievalModel, GenerationModel
from langchain_core.documents import Document
from cache_redis import get_cache
from graphs import create_main_graph
from fastapi import APIRouter, HTTPException
import json
import os
# import asyncio

## STEP 3. EVALUATE !!


router = APIRouter()


def cleanse_data(data):
    # data = [{}]
    query = []
    predicted_documents = []
    ground_truth_documents = []
    
    ground_truth_answer=[]
    retrieved_contexts=[]
    generated_answer=[]
    
    for row in data.keys(): 
        if row == "query":
            query.append(data[row])
    
    
    return 

def to_document(chunks: List[List[str]]) -> List[Document]:
    return [
        Document(
            page_content=chunk["text"],
            file_name=chunk["file_name"],
            metadata={k: v for k, v in chunk.items() if k != "text"},
        )
        for chunk in chunks
    ]
    
    
def create_input_payload(request):
    
    stored_session_json = get_cache(request.session_id)
    if not stored_session_json:
        raise HTTPException(status_code=404, detail="Session not found or has expired.")
    session_data = json.loads(stored_session_json)
    
    config = session_data["config"]
    benchmark_dataset = session_data["benchmark_dataset"]
    
    print(config)
    print(benchmark_dataset)
    
    if not config or not benchmark_dataset:
        raise ValueError("Configuration or benchmark_dataset is missing.")
    
    retrieval_dataset = None 
    generation_dataset = None
    
    if isinstance(benchmark_dataset, RetrievalModel):
        print("Dataset type is 'RetrievalModel'. Populating retrieval payload.")
        retrieval_dataset = {
            "query": benchmark_dataset.query,
            "predicted_documents": to_document(benchmark_dataset.predicted_documents),
            "ground_truth_documents": to_document(benchmark_dataset.ground_truth_documents), # List[List of text]
            "model": config.model,
            "k": config.top_k,
        }
        
    elif isinstance(benchmark_dataset, GenerationModel):
        print("Dataset type is 'GenerationModel'. Populating generation payload.")
        generation_dataset = {
            "query": benchmark_dataset.query,
            "ground_truth_answer": benchmark_dataset.ground_truth_answer,
            "retrieved_contexts": benchmark_dataset.retrieved_contexts,
            "generated_answer": benchmark_dataset.generated_answer,
            "model": config.model,
        }
    else:
        raise TypeError(f"Unsupported dataset type: {type(benchmark_dataset).__name__}")

    final_payload = {
        "retrieve_metrics": config.retrieval_metrics,
        "generate_metrics": config.generation_metrics,
        "dataset": {
            "Retrieval": retrieval_dataset,
            "Generation": generation_dataset,
        },
            "evaluation_mode": config.evaluation_mode,
    }

    return final_payload


@router.post("/", status_code=202)
async def evaluator(evaluation_request: EvaluationRequest):

    # if not (evaluation_request["session_id"] or evaluation_request["user_id"]):
    #     raise HTTPException(status_code=404, detail="Evaluation request Invalid!")
    graph_input = create_input_payload(evaluation_request)

    main_graph = create_main_graph()
    response = await main_graph.ainvoke(input=graph_input)
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    print(retrieval_evaluation_result, generator_evaluation_result)
    return retrieval_evaluation_result, generator_evaluation_result

