# from krag.document import KragDocument
# from krag.evaluators import OfflineRetrievalEvaluators

# # 각 쿼리에 대한 정답 문서 
# actual_docs = [
#     #  Query 1
#     [
#         KragDocument(metadata={'id': 1}, page_content='1'),
#         KragDocument(metadata={'id': 2}, page_content='2'),
#         KragDocument(metadata={'id': 3}, page_content='3'),
#     ],
#     #  Query 2
#     [
#         KragDocument(metadata={'id': 4}, page_content='4'),
#         KragDocument(metadata={'id': 5}, page_content='5'),
#         KragDocument(metadata={'id': 6}, page_content='6'),
#     ],
#     #  Query 3
#     [
#         KragDocument(metadata={'id': 7}, page_content='7'),
#         KragDocument(metadata={'id': 8}, page_content='8'),
#         KragDocument(metadata={'id': 9}, page_content='9'),
#     ],
# ]


# # 각 쿼리에 대한 검색 결과 
# predicted_docs = [
#     #  Query 1
#     [
#         KragDocument(metadata={'id': 1}, page_content='1'),
#         KragDocument(metadata={'id': 4}, page_content='4'),
#         KragDocument(metadata={'id': 7}, page_content='7'),
#         KragDocument(metadata={'id': 2}, page_content='2'),
#         KragDocument(metadata={'id': 5}, page_content='5'),
#         KragDocument(metadata={'id': 8}, page_content='8'),
#         KragDocument(metadata={'id': 3}, page_content='3'),
#         KragDocument(metadata={'id': 6}, page_content='6'),
#         KragDocument(metadata={'id': 9}, page_content='9')
#     ],

#     #  Query 2
#     [
#         KragDocument(metadata={'id': 4}, page_content='4'),
#         KragDocument(metadata={'id': 1}, page_content='1'),
#         KragDocument(metadata={'id': 7}, page_content='7'),
#         KragDocument(metadata={'id': 5}, page_content='5'),
#         KragDocument(metadata={'id': 2}, page_content='2'),
#         KragDocument(metadata={'id': 8}, page_content='8'),
#         KragDocument(metadata={'id': 6}, page_content='6'),
#         KragDocument(metadata={'id': 3}, page_content='3'),
#         KragDocument(metadata={'id': 9}, page_content='9')
#     ],
    
#     #  Query 3
#     [
#         KragDocument(metadata={'id': 7}, page_content='7'),
#         KragDocument(metadata={'id': 2}, page_content='2'),
#         KragDocument(metadata={'id': 4}, page_content='4'),
#         KragDocument(metadata={'id': 8}, page_content='8'),
#         KragDocument(metadata={'id': 5}, page_content='5'),
#         KragDocument(metadata={'id': 3}, page_content='3'),
#         KragDocument(metadata={'id': 9}, page_content='9'),
#         KragDocument(metadata={'id': 6}, page_content='6'),
#         KragDocument(metadata={'id': 1}, page_content='1')
#     ]
# ]


# # Initialize the evaluator / 평가도구 초기화 
# evaluator = OfflineRetrievalEvaluators(actual_docs, predicted_docs, match_method="rouge1")

# # Calculate evaluation metrics / 평가지표 계산 
# hit_rate = evaluator.calculate_hit_rate()
# mrr = evaluator.calculate_mrr()
# recall_at_3 = evaluator.calculate_recall_k(k=3)
# precision_at_5 = evaluator.calculate_precision_k(k=5)
# map_at_5 = evaluator.calculate_map_k(k=5)
# ndcg_at_5 = evaluator.ndcg_at_k(k=5)

# # Print results / 결과 출력
# print(f"Hit Rate: {hit_rate}")
# print(f"MRR: {mrr}")
# print(f"Recall@3: {recall_at_3}")
# print(f"Precision@5: {precision_at_5}")
# print(f"MAP@5: {map_at_5}")
# print(f"NDCG@5: {ndcg_at_5}")