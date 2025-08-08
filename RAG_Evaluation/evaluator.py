from pathlib import Path
from graphs import create_main_graph
from pathlib import Path
from utils import dataprocess_retrieve, dataprocess_generate
from schema import EvaluationSchema


PATH = Path(".").resolve() / "data"
EXAMPLE_DATASET = PATH / "response_merged_output.csv"


"""
RETRIEVAL DATA: Retrieved Documents, Answer Documents
GENERATED DATA: User Query, Reference Document, Answer Response, LLM Response

"""


async def evaluator(payload: EvaluationSchema):
    data = payload.get("dataset")
    retrieval_data = data.get("Retrieval")
    generation_data = data.get("Generation")
    config = payload.get("config")

    predicted_docs, actual_docs = dataprocess_retrieve(EXAMPLE_DATASET)
    query, reference, retrieved_contexts, _response = dataprocess_generate(
        EXAMPLE_DATASET
    )
    main_graph = create_main_graph()
    response = await main_graph.ainvoke(
        {
            "retrieve_metrics": [
                "mrr",
                "map",
                "f1",
                "ndcg",
                "precision",
                "recall",
            ],  # "mrr" "map", "f1", "ndcg", "precision", "recall"
            "generate_metrics": ["bleu"],  # 'bleu', 'rouge','faithfulness'
            "dataset": {
                "Retrieval": {
                    "predicted_documents": predicted_docs,  # List[Document(metadata={}, page_content=content)]
                    "actual_documents": actual_docs,  # List[List[Document(metadata={}, page_content=content)]]
                    "k": 5,
                },
                "Generation": {
                    "query": query,  # dataset['question'] List[str]
                    "reference": reference,  # dataset['target_answer'] List[List[Document|str]]
                    "retrieved_contexts": retrieved_contexts,  # dataset['target_file_name']  List[List[Document | str]],
                    "response": _response,  # dataset['alli_gpt-4-turbo_answer'] List[str],
                    "model": "azure",  # str
                },
            },
            "evaluation_mode": "generation_only",  # "retrieval_only", "generation_only", "full"
        }
    )
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    return retrieval_evaluation_result, generator_evaluation_result
