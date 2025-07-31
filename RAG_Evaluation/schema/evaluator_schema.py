from pydantic import BaseModel, Field
from langchain_core.documents import Document
from typing import List, Literal


class RetrievalModel(BaseModel):
    """
    Pydantic model for the 'Retrieval' part of the dataset.
    It contains the predicted and actual document IDs for retrieval metric calculation.
    """

    predicted_documents: List[Document] = Field(
        ..., description="List of predicted document IDs."
    )
    actual_documents: List[List[Document]] = Field(
        ..., description="List of ground truth document IDs."
    )
    k: int = Field(
        ..., description="The number of top documents considered for retrieval metrics."
    )


class GenerationModel(BaseModel):
    """
    Pydantic model for the 'Generation' part of the dataset.
    It contains the necessary inputs and outputs for generation metric calculation.
    """

    query: List[str] = Field(..., description="The input query or question.")
    reference: List[List[Document|str]] = Field(..., description="The ground truth or reference answer.")
    retrieved_contexts: List[List[Document|str]] = Field(
        ..., description="The list of context strings passed to the generator."
    )
    response: List[str] = Field(..., description="The generated response from the RAG model.")
    model: str = Field(
        ...,
        description="Identifier for the model used for generation (e.g., 'azure', 'openai').",
    )


class DatasetModel(BaseModel):
    """
    Pydantic model that encapsulates both the Retrieval and Generation data.
    """

    Retrieval: RetrievalModel
    Generation: GenerationModel


class EvaluationSchema(BaseModel):
    """
    The main Pydantic model for the entire evaluation payload.
    This structure is expected by the /evaluate endpoint.
    """

    retrieve_metrics: List[
        Literal["mrr", "map", "f1", "ndcg", "precision", "recall"]
    ] = Field(..., description="A list of retrieval metrics to be calculated.")
    generate_metrics: List[Literal["bleu", "rouge", "faithfulness"]] = Field(
        ..., description="A list of generation metrics to be calculated."
    )
    dataset: DatasetModel = Field(
        ..., description="The dataset containing retrieval and generation data."
    )
    evaluation_mode: Literal["retrieval_only", "generation_only", "full"] = Field(
        ..., description="The evaluation mode to run."
    )


# Example usage:
# The user's provided JSON structure can be directly parsed into this model.
json_payload = {
    "retrieve_metrics": ["mrr", "map", "precision", "recall"],
    "generate_metrics": ["bleu", "faithfulness"],
    "dataset": {
        "Retrieval": {
            "predicted_documents": ["doc_3", "doc_1", "doc_5"],
            "actual_documents": ["doc_1", "doc_2"],
            "k": 5,
        },
        "Generation": {
            "query": "What is RAG?",
            "reference": "Retrieval-Augmented Generation is a technique...",
            "retrieved_contexts": [
                "...context from doc_3...",
                "...context from doc_1...",
            ],
            "response": "RAG is a method that combines retrieval with generation...",
            "model": "azure",
        },
    },
    "evaluation_mode": "full",
}

try:
    # FastAPI will do this automatically in the request body
    parsed_payload = EvaluationSchema(**json_payload)
    print("Payload parsed successfully!")
    print(parsed_payload.model_dump_json(indent=2))
except Exception as e:
    print(f"Error parsing payload: {e}")
