from typing import List, Dict, Any

def cleanse_data(data: List[Dict[str, Any]]) -> Dict[str, List]:

    query = []
    predicted_documents = []
    ground_truth_documents = []
    
    ground_truth_answer = []
    retrieved_contexts = []
    generated_answer = []


    for row in data:

        if "query" in row:
            query.append(row.get("query"))
            
        if "predicted_documents" in row:
            predicted_documents.append(row.get("predicted_documents", []))
            
        if "ground_truth_documents" in row:
            ground_truth_documents.append(row.get("ground_truth_documents", []))

        if "ground_truth_answer" in row:
            ground_truth_answer.append(row.get("ground_truth_answer", []))
            
        if "retrieved_contexts" in row:
            retrieved_contexts.append(row.get("retrieved_contexts", []))
            
        if "generated_answer" in row:
            generated_answer.append(row.get("generated_answer"))

    return {
        "query": query,
        "predicted_documents": predicted_documents,
        "ground_truth_documents": ground_truth_documents,
        "ground_truth_answer": ground_truth_answer,
        "retrieved_contexts": retrieved_contexts,
        "generated_answer": generated_answer
    }

if __name__ == "__main__":
    sample_data = [
        {
            "query": "What is Polars?",
            "predicted_documents": ["Doc A", "Doc B"],
            "ground_truth_documents": [["Doc A"]],
            "generated_answer": "Polars is a DataFrame library."
        },
        {
            "query": "What is FastAPI?",
            "predicted_documents": ["Doc C"],
            "ground_truth_documents": [["Doc C", "Doc D"]],
            "generated_answer": "FastAPI is a web framework."
        }
    ]

    cleansed_data = cleanse_data(sample_data)
    
    print("--- Cleansed and Separated Data ---")
    import json
    print(json.dumps(cleansed_data, indent=2))