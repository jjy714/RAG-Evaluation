from pathlib import Path
from typing import List
from schema import EvaluationRequest, GraphSchema, RetrievalModel, GenerationModel
from langchain_core.documents import Document
from SHARED_PROCESS import SHARED_PROCESS
from graphs import create_main_graph
from utils import dataprocess_retrieve, dataprocess_generate
from uuid import uuid4
from fastapi import APIRouter, HTTPException, File, UploadFile
import os

# import asyncio


router = APIRouter()
"""
RETRIEVAL DATA: Retrieved Documents, Answer Documents
GENERATED DATA: User Query, Reference Document, Answer Response, LLM Response
"""
predicted_docs, actual_docs = dataprocess_retrieve(EXAMPLE_DATASET)
query, reference, retrieved_contexts, _response = dataprocess_generate(EXAMPLE_DATASET)


def to_document(chunks: RetrievalModel | GenerationModel) -> List[Document]:
    return [
        Document(
            page_content=chunk["text"],
            file_name=chunk["file_name"],
            metadata={k: v for k, v in chunk.items() if k != "text"},
        )
        for chunk in chunks
    ]


def create_input_payload():
    config = SHARED_PROCESS["session_id"]["config"]
    benchmark_dataset = SHARED_PROCESS["session_id"]["benchmark_dataset"]
    
    if not config or not benchmark_dataset:
        raise ValueError("Configuration or benchmark_dataset is missing.")

    # Initialize payloads with default None values
    
    retrieval_dataset = None 
    generation_dataset = None
    
    if isinstance(benchmark_dataset, RetrievalModel):
        print("Dataset type is 'RetrievalModel'. Populating retrieval payload.")
        # 2. Populate the correct dictionary based on the type
        retrieval_dataset = {
            "user_input": benchmark_dataset.user_input,
            "predicted_documents": to_document(benchmark_dataset.predicted_documents),
            "actual_documents": to_document(benchmark_dataset.actual_documents), # List[List of text]
            "model": config.model,
            "k": config.top_k,
        }
    elif isinstance(benchmark_dataset, GenerationModel):
        print("Dataset type is 'GenerationModel'. Populating generation payload.")
        # 2. Populate the other dictionary based on the type
        generation_dataset = {
            "query": benchmark_dataset.query,
            "reference": benchmark_dataset.reference,
            "retrieved_contexts": benchmark_dataset.retrieved_contexts,
            "response": benchmark_dataset.response,
            "model": config.model,
        }
    else:
        # It's good practice to handle unexpected types
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

@router.post("/evaluate", status_code=202)
async def evaluator(evaluation_request: EvaluationRequest):

    if not (evaluation_request["session_id"] or evaluation_request["user_id"]):
        raise HTTPException(status_code=404, detail="Evaluation request Invalid!")

    session_id = evaluation_request["session_id"]
    config = SHARED_PROCESS[session_id]["config"]
    benchmark_data = SHARED_PROCESS[session_id]["benchmark_data"]

    predicted_docs, actual_docs = dataprocess_retrieve(file)
    query, reference, retrieved_contexts, _response = dataprocess_generate(file)

    main_graph = create_main_graph()
    response = await main_graph.ainvoke(
        input={
            "retrieve_metrics": [
                "mrr",
                "map",
                "f1",
                "ndcg",
                "precision",
                "recall",
            ],  # "mrr" "map", "f1", "ndcg", "precision", "recall"
            "generate_metrics": ["bleu", "rouge"],  # 'bleu', 'rouge','faithfulness'
            "dataset": {
                "Retrieval": {
                    "user_input": None,
                    "predicted_documents": predicted_docs,  # List[Document(metadata={}, page_content=content)]
                    "actual_documents": actual_docs,  # List[List[Document(metadata={}, page_content=content)]]
                    "model": "None",
                    "k": 5,
                },
                "Generation": {
                    "query": query,  # dataset['question'] List[str]
                    "reference": reference,  # dataset['target_answer'] List[List[Document|str]]
                    "retrieved_contexts": retrieved_contexts,  # dataset['target_file_name']  List[List[Document | str]],
                    "response": _response,  # dataset['alli_gpt-4-turbo_answer'] List[str],
                    "model": "none",  # str azure
                },
            },
            "evaluation_mode": "full",  # "retrieval_only", "generation_only", "full"
        }
    )
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    print(retrieval_evaluation_result, generator_evaluation_result)
    return retrieval_evaluation_result, generator_evaluation_result


# if __name__ == '__main__':
#     asyncio.run(evaluator(payload=payload))
