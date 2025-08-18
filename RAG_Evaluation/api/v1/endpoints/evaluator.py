from pathlib import Path
from graphs import create_main_graph
from pathlib import Path
from utils import dataprocess_retrieve, dataprocess_generate
import asyncio

# from schema import EvaluationSchema, EvaluationRequest
from uuid import uuid4
from fastapi import APIRouter, HTTPException
import os 
router = APIRouter

PATH = "/Users/jason/Claion/RAG/RAG_Evaluation/RAG_Evaluation/data"
EXAMPLE_DATASET = os.path.join(PATH, "response_merged_output.csv")


"""
RETRIEVAL DATA: Retrieved Documents, Answer Documents
GENERATED DATA: User Query, Reference Document, Answer Response, LLM Response
"""
predicted_docs, actual_docs = dataprocess_retrieve(EXAMPLE_DATASET)
query, reference, retrieved_contexts, _response = dataprocess_generate(EXAMPLE_DATASET)
payload = {
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


# @router.post("/evaluate", response_model=EvaluationStartResponse, status_code=202)
async def evaluator(payload):
    # data = payload.get("dataset")
    # retrieval_data = data.get("Retrieval")
    # generation_data = data.get("Generation")
    # config = payload.get("config")


    main_graph = create_main_graph()
    response = await main_graph.ainvoke(payload)
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    print(retrieval_evaluation_result, generator_evaluation_result)
    return retrieval_evaluation_result, generator_evaluation_result



if __name__ == '__main__':
    asyncio.run(evaluator(payload=payload))