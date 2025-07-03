


def mrr(self, retrieved_docs, ground_truth_ids):
        
        reciprocal_ranks = []

    # Iterate through each query's results
        for i, retrieved in enumerate(retrieved_docs):
            relevant_ids_for_query = set(ground_truth_ids[i])
            
            # Sort retrieved documents by rank to be sure
            sorted_retrieved = sorted(retrieved, key=lambda x: x['rank'])
            
            rank = 0
            for doc in sorted_retrieved:
                if doc['doc_id'] in relevant_ids_for_query:
                    # Found the first relevant document, calculate reciprocal rank and break
                    rank = doc['rank']
                    reciprocal_ranks.append(1.0 / rank)
                    break
            
            # If no relevant document was found for this query, rank is 0
            if rank == 0:
                reciprocal_ranks.append(0.0)

        # Calculate the mean of all reciprocal ranks
        mrr_score = np.mean(reciprocal_ranks) if reciprocal_ranks else 0.0
        return mrr_score
            