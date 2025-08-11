# import numpy as np


# def mrr(retrieved_docs, ground_truth_ids):
#     mrr_score = 0
#     rr = []
#     for idx, docs in enumerate(retrieved_docs):
#         rank = 0
#         id = ground_truth_ids[idx] #str
#         for _, doc in enumerate(docs): 
#             if id in doc: 
#                 rank = _ + 1
#                 rr.append(1.0 / rank)
#                 break
#         if rank == 0:
#             rr.append(0.0)        
        
#     mrr_score = np.mean(rr) if rr else 0.0
#     return mrr_score
                
            