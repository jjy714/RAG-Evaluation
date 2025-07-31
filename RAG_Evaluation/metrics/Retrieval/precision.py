
from ragas.metrics import NonLLMContextPrecisionWithReference
from ragas import SingleTurnSample



async def precision():
    context_precision = NonLLMContextPrecisionWithReference()

    sample = SingleTurnSample(
        retrieved_contexts=["The Eiffel Tower is located in Paris."], 
        reference_contexts=["Paris is the capital of France.", "The Eiffel Tower is one of the most famous landmarks in Paris."]
    )

    await context_precision.single_turn_ascore(sample)


def precision_at_k(retrieved_docs, ground_truth_ids, k) -> float:
    """
    Calculates the Mean Precision@K for a set of queries.

    Precision@K is the proportion of retrieved documents in the top K
    that are relevant.
    """
    all_precisions_at_k = []
    for i, retrieved in enumerate(retrieved_docs):
        relevant_ids_for_query = set(ground_truth_ids[i])
        top_k_docs = sorted([d for d in retrieved if d['rank'] <= k], key=lambda x: x['rank'])
        
        hits = 0
        for doc in top_k_docs:
            if doc['doc_id'] in relevant_ids_for_query:
                hits += 1
        
        precision_at_k = hits / k if k > 0 else 0.0
        all_precisions_at_k.append(precision_at_k)
        
    return np.mean(all_precisions_at_k) if all_precisions_at_k else 0.0
