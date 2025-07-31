DATATYPE: {
    predicted_documents: List[List[Document]],
    actual_documents: List[List[Document]],
    metrics_to_run: List[str],
    k: int,
    # --- INTERNAL STATE ---
    evaluator: Optional[RetrievalEvaluator],

    # --- OUTPUT ---
    mrr_score: Optional[float],
    map_score: Optional[float],
    ndcg_score: Optional[float],

    precision_micro: Optional[float],
    precision_macro: Optional[float],
    recall_micro: Optional[float],
    recall_macro: Optional[float],
    f1_micro: Optional[float],
    f1_macro: Optional[float],

    final_results: Dict[str, float],




}