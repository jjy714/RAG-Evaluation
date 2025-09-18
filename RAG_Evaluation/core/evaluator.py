from langchain_core.documents import Document
from typing import Dict, List, Any
from cache_redis import get_cache, set_cache
from fastapi import HTTPException
import json 


# FOR PROTOTYPING DEMONSTRATION. NEEDS TO BE GENERALIZED
def _create_document(page_content: str, file_name: str | None, page_num: int | None) -> Document | None:
    if not page_content:
        return None
    
    metadata = {
        'file_name': file_name,
        'page': page_num
    }
    clean_metadata = {k: v for k, v in metadata.items() if v is not None}
    return Document(page_content=page_content, metadata=clean_metadata)

def cleanse_data(data: List[Dict[str, Any]], max_retrieved_docs: int = 5) -> Dict[str, List]:
    queries = []
    predicted_documents_batch = []
    ground_truth_documents_batch = []
    ground_truth_answers = []
    generated_answers = []

    for row in data:
        queries.append(row.get("question"))
        ground_truth_answers.append(row.get("target_answer"))
        generated_answers.append(row.get("response"))

        current_ground_truth_docs = []
        gt_doc = _create_document(
            page_content=row.get("target_answer"),
            file_name=row.get("target_file_name"),
            page_num=row.get("target_page_no")
        )
        if gt_doc:
            current_ground_truth_docs.append(gt_doc)
        ground_truth_documents_batch.append(current_ground_truth_docs)

        current_predicted_docs = []
        for i in range(1, max_retrieved_docs + 1):
            doc_key = f'retrieved_doc{i}'
            cont_key = f'retrieved_cont{i}'
            page_key = f'retrieved_page{i}'

            pred_doc = _create_document(
                page_content=row.get(cont_key),
                file_name=row.get(doc_key),
                page_num=row.get(page_key)
            )
            if pred_doc:
                current_predicted_docs.append(pred_doc)
        
        predicted_documents_batch.append(current_predicted_docs)

    return {
        "query": queries,
        "predicted_documents": predicted_documents_batch,
        "ground_truth_documents": ground_truth_documents_batch,
        "ground_truth_answer": ground_truth_answers,
        "generated_answer": generated_answers
    }
# def to_document(chunks: List[List[str]]) -> List[Document]:
#     return [
#         Document(
#             page_content=chunk["text"],
#             file_name=chunk["file_name"],
#             metadata={k: v for k, v in chunk.items() if k != "text"},
#         )
#         for chunk in chunks
#     ]
    
    
# def to_document(list_of_list_of_strings: List[List[str]]) -> List[Document]:
#     return [
#         Document(
#             page_content=list_of_strings,
#         )
#         for list_of_strings in list_of_list_of_strings
#     ]    
    
    
def create_input_payload(request):
    stored_session_json = get_cache(request.session_id)
    if not stored_session_json:
        raise HTTPException(status_code=404, detail="Session not found or has expired.")
    session_data = json.loads(stored_session_json)
    
    print(session_data)
    config = session_data["config"]
    config = json.loads(config)
    benchmark_dataset = session_data["benchmark_dataset"]
    
    if not config or not benchmark_dataset:
        raise ValueError("Configuration or benchmark_dataset is missing.")
    
    cleansed_data = cleanse_data(benchmark_dataset)
    
    retrieval_dataset = None 
    generation_dataset = None
    
    print("Dataset type is 'RetrievalModel'. Populating retrieval payload.")
    retrieval_dataset = {
        "query": cleansed_data.get("query", []),
        "predicted_documents": cleansed_data.get("predicted_documents", []),
        "ground_truth_documents": cleansed_data.get("ground_truth_documents", []), # List[List of text]
        "model": config.get("model", ""),
        "k": config.get("top_k", ""),
    }
    
    print("Dataset type is 'GenerationModel'. Populating generation payload.")
    generation_dataset = {
        "query": cleansed_data.get("query", []),
        "ground_truth_answer": cleansed_data.get("ground_truth_answer", []),
        "retrieved_contexts": cleansed_data.get("retrieved_contexts", []),
        "generated_answer": cleansed_data.get("generated_answer", []),
        "model": config.get("model", ""),
    }

    final_payload = {
        "retrieve_metrics": config.get("retrieve_metrics", []),
        "generate_metrics":config.get("generate_metrics", []),
        "session_id": request.session_id,
        "dataset": {
            "Retrieval": retrieval_dataset,
            "Generation": generation_dataset,
        },
            "evaluation_mode": config.get("evaluation_mode", ""),
    }

    return final_payload
