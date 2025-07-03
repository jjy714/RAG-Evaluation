

def map(self, retrieved_docs, ground_truth_ids) -> float:
        """
        Calculates the Mean Average Precision (MAP) for a set of queries.

        MAP provides a more comprehensive measure than MRR by considering the
        precision at each relevant document's position.
        """
        average_precisions = []
        for i, retrieved in enumerate(retrieved_docs):
            relevant_ids_for_query = set(ground_truth_ids[i])
            if not relevant_ids_for_query:
                average_precisions.append(0.0)
                continue
            sorted_retrieved = sorted(retrieved, key=lambda x: x['rank'])
            hits = 0
            precisions_at_k = []
            for k, doc in enumerate(sorted_retrieved, 1):
                if doc['doc_id'] in relevant_ids_for_query:
                    hits += 1
                    precision_at_k = hits / k
                    precisions_at_k.append(precision_at_k)
            if not precisions_at_k:
                average_precisions.append(0.0)
            else:
                average_precisions.append(np.mean(precisions_at_k))
        return np.mean(average_precisions) if average_precisions else 0.0