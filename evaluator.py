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

PATH = Path(".").resolve() / "data/results"
EXAMPLE_DATASET = PATH / "03-01_bmt_result.csv"


# action="store_true"
# parser = argparse.ArgumentParser()
# parser.add_argument("-m", "--metrics", type=str, help="Which Metrics to evaluate")
# parser.add_argument("-d", "--dataset", type=str, help="Dataset to evaluate on")
# parser.add_argument(
#     "-M", "--mode", type=str, help="Evaluate on Retrieval, Generator, or Overall"
# )
# args = parser.parse_args()


def evaluator():
    """
    MAIN GRAPH:
        class EvaluationState(TypedDict):
            retrieve_metrics: List[str] | None
            generate_metrics: List[str] | None
            dataset: Dataset | List
            evaluation_mode: str
            retriever_evaluation_result = Dict
            generator_evaluation_result = Dict

    RETRIEVAL SUBGRAPH:
        class RetrievalEvaluationState(TypedDict):
            # --- INPUTS ---
            predicted_documents: List[List[Document]]
            actual_documents: List[List[Document]]
            metrics_to_run: List[str]
            k: int

            # --- INTERNAL STATE ---
            evaluator: Optional[RetrievalEvaluator]

            # --- OUTPUT ---
            mrr_score: Optional[float]
            precision_score: Optional[float]
            recall_score: Optional[float]
            f1_score: Optional[float]
            ndcg_score: Optional[float]
            final_results: Dict[str, float]
    """

    # dataset = load_dataset(args.dataset)
    # dataset = load_dataset(EXAMPLE_DATASET)
    # metrics = args.metrics.split(",")
    # selected_metrices=args.mode.split(",")
    df = pd.read_csv(EXAMPLE_DATASET)

    questions = df.loc[:, ["question"]]
    target_docs_names = df.loc[:, "target_file_name"]
    target_docs_names = target_docs_names.values.tolist()

    retrieved_docs = df.loc[
        :,
        [
            "retrieved_doc1",
            "retrieved_doc2",
            "retrieved_doc3",
            "retrieved_doc4",
            "retrieved_doc5",
        ],
    ]
    retrieved_docs = retrieved_docs.values.tolist()

    actual_docs = []
    predicted_docs=[]

    for content in target_docs_names:
        actual_docs.append([Document(metadata={}, page_content=content)])
    for id, content in enumerate(retrieved_docs):
        temp = []
        for i in content:
            temp.append(Document(metadata={}, page_content=i))
        predicted_docs.append(temp)

    # print("ACTUAL DOCUMENT")
    # print(actual_docs)
    # print("PREDICTED DOCUMENT")
    # print(predicted_docs)
    main_graph = create_main_graph()
    response = main_graph.invoke(
        {
            "retrieve_metrics": ["mrr", "map", "f1", "ndcg","precision", "recall"], #"mrr" "map", "f1", "ndcg", "precision", "recall"
            "generate_metrics": ['bleu', 'rouge','faithfulness'],
            "dataset": {
                "Retrieval": {
                    "predicted_documents": predicted_docs,
                    "actual_documents": actual_docs,
                    "k": 5,
                },
                "Generation": {
                    "user_input":"",
                    "reference": "",
                    "retrieved_contexts": "",
                    "response":"",
                    "model":"azure"
                    },
            },
            "evaluation_mode": "generation_only", # "retrieval_only", "generation_only", "full"
        }
    )
    print(f"Retriever Evaluation Result : {response.get("retriever_evaluation_result")}")
    print(f"Generator Evaluation Result : {response.get("generator_evaluation_result")}")
    

if __name__ == "__main__":
    evaluator()
