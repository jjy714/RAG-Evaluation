import argparse
import datasets
from pathlib import Path
from dotenv import load_dotenv
from datasets import load_dataset, Dataset
from graphs import create_main_graph
from typing import Dict
from langchain_core.documents import Document
import pandas as pd
from datasets import load_dataset
from pathlib import Path
from pydantic import BaseModel
from utils import dataprocess_retrieve, dataprocess_generate
from schema import EvaluationSchema
import asyncio



PATH = Path(".").resolve() / "data"
EXAMPLE_DATASET = PATH / "response_merged_output.csv"


# action="store_true"
# parser = argparse.ArgumentParser()
# parser.add_argument("-m", "--metrics", type=str, help="Which Metrics to evaluate")
# parser.add_argument("-d", "--dataset", type=str, help="Dataset to evaluate on")
# parser.add_argument(
#     "-M", "--mode", type=str, help="Evaluate on Retrieval, Generator, or Overall"
# )
# args = parser.parse_args()



async def evaluator(payload: EvaluationSchema):
    data = payload.get("dataset")
    retrieval_data = data.get("Retrieval")
    generation_data = data.get("Generation")
    config = payload.get("config")

    predicted_docs, actual_docs = dataprocess_retrieve(EXAMPLE_DATASET)
    query, reference, retrieved_contexts, _response = dataprocess_generate(EXAMPLE_DATASET)
    main_graph = create_main_graph()
    response = await main_graph.ainvoke(
        {
            "retrieve_metrics": ["mrr", "map", "f1", "ndcg","precision", "recall"], #"mrr" "map", "f1", "ndcg", "precision", "recall"
            "generate_metrics": ['bleu'], # 'bleu', 'rouge','faithfulness'
            "dataset": {
                "Retrieval": {
                    "predicted_documents": predicted_docs, # List[Document(metadata={}, page_content=content)]
                    "actual_documents": actual_docs, # List[List[Document(metadata={}, page_content=content)]]
                    "k": 5,
                },
                "Generation": {
                    "query": query, # dataset['question'] List[str]
                    "reference": reference, #dataset['target_answer'] List[List[Document|str]] 
                    "retrieved_contexts": retrieved_contexts , #dataset['target_file_name']  List[List[Document | str]],
                    "response": _response, #dataset['alli_gpt-4-turbo_answer'] List[str],
                    "model":"azure" # str
                    },
            },
            "evaluation_mode": "generation_only", # "retrieval_only", "generation_only", "full"
        }
    )
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    return retrieval_evaluation_result, generator_evaluation_result    

