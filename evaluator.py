import argparse
import datasets
from pathlib import Path
from dotenv import load_dotenv
from datasets import load_dataset, Dataset
from graphs import create_main_graph
from langchain_core.documents import Document
import pandas as pd
from datasets import load_dataset
from pathlib import Path
from utils import dataprocess_retrieve, dataprocess_generate
import json
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


async def evaluator():
    
    # dataset = load_dataset(args.dataset)
    # dataset = load_dataset("allganize/RAG-Evaluation-Dataset-KO", split="test[:10]")
    # metrics = args.metrics.split(",")
    # selected_metrices=args.mode.split(",")
    
    predicted_docs, actual_docs = dataprocess_retrieve(EXAMPLE_DATASET)
    query, reference, retrieved_contexts, _response = dataprocess_generate(EXAMPLE_DATASET)
    main_graph = create_main_graph()
    response = await main_graph.ainvoke(
        {
            "retrieve_metrics": ["mrr", "map", "f1", "ndcg","precision", "recall"], #"mrr" "map", "f1", "ndcg", "precision", "recall"
            "generate_metrics": ['bleu'], # 'bleu', 'rouge','faithfulness'
            "dataset": {
                "Retrieval": {
                    "predicted_documents": predicted_docs,
                    "actual_documents": actual_docs,
                    "k": 5,
                },
                "Generation": {
                    "query": query, # dataset['question']
                    "reference": reference, #dataset['target_answer']
                    "retrieved_contexts": retrieved_contexts , #dataset['target_file_name']
                    "response": _response, #dataset['alli_gpt-4-turbo_answer']
                    "model":"azure"
                    },
            },
            "evaluation_mode": "retrieval_only", # "retrieval_only", "generation_only", "full"
        }
    )
    print(f"Retriever Evaluation Result : {json.dumps(response.get("retriever_evaluation_result"))}")
    print(f"Generator Evaluation Result : {response.get("generator_evaluation_result")}")
    

if __name__ == "__main__":
    asyncio.run(evaluator())
