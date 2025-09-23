from langchain_core.documents  import Document
from ..krag._evaluators import OfflineRetrievalEvaluators
from .context_relevance import context_relevance
from langchain_openai import ChatOpenAI, AzureChatOpenAI
# from .MRR import map 
# from .MRR import mrr
# from .precision import precision, precision_at_k
# from .recall import recall, recall_as_llm
# from .noise_sensitivity import noise_sensitivity
# from .response_relevancy import response_relevancy
from typing import Union, List, Dict, Optional, Any
from enum import Enum
from cache_redis import set_cache
import httpx
import asyncio

# TODO: path 변경
from core.post_data import DataPointApiClient

# from .accuracy 
# class ApiClient:
#     def __init__(self, session_id: str, endpoint: str):
#         self.endpoint = endpoint
#         self.session_id = session_id
#         print(f"API Client initialized for endpoint: {self.endpoint}")
        
        
#     def send_redis(self, data, error): 
#         return set_cache(session_id=self.session_id, input=(data, error))

#     async def send_dashboard(self, payload: Dict[str, Any]):
#         """Sends a single metric data point to the dashboard API."""
#         async with httpx.AsyncClient() as client:    
#             try:
#                 response = client.post(self.endpoint, json=payload)
#                 response.raise_for_status()
#                 print(f"Successfully sent metric: {payload['metric_name']}")
#             except client.RequestException as e:
#                 print(f"Error sending metric to dashboard: {e}")
#         return response


class AveragingMethod(Enum):
    MICRO = "micro"
    MACRO = "macro"
    BOTH = "both"

class MatchingCriteria(Enum):
    ALL = "all"
    PARTIAL = "partial"

class RetrievalEvaluator(OfflineRetrievalEvaluators):

    def __init__(
            self,
            query: List[str],
            ground_truth_documents: List[List[Document]], 
            predicted_documents: List[List[Document]],
            model: ChatOpenAI | AzureChatOpenAI,
            
            session_id: str, 
            endpoint: str,
            
                        
            match_method: str = "text", 
            averaging_method: Union[str, AveragingMethod] = AveragingMethod.BOTH,
            matching_criteria: MatchingCriteria = MatchingCriteria.ALL,
            ):
        super().__init__(
            actual_docs=ground_truth_documents, 
            predicted_docs=predicted_documents, 
            match_method= match_method, 
            averaging_method=averaging_method, 
            matching_criteria=matching_criteria
        )
        
        # self.sender = ApiClient(session_id=session_id, endpoint=endpoint)
        self.sender_temp = DataPointApiClient(session_id=session_id, endpoint=endpoint)
        
        self.query = query
        self.model = model
        self.predicted_docs = predicted_documents
        
        self.actual_docs = ground_truth_documents
        self.predicted_docs = predicted_documents
        
        
    async def f1(self, k:int=5) -> List[Dict[str, float]]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        f1_result = []
        for i in range(len(self.query)):
            temp = self.calculate_f1_score(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k)
            # => send_dashboard()
            await self.sender_temp.send_dashboard(payload={"metric_name": "f1", "score": [temp.get("micro_f1"), temp.get("macro_f1")]})

            temp = (temp.get("micro_f1"), temp.get("macro_f1"), temp.get("zero_score_indexes"))
            print(f"-----[{i}] F1 RESULT: {temp} -----")
            # self.sender.send_redis() 
            f1_result.append(temp)
        
        self.sender_temp.send_redis(payload={"metric_name": "f1", "score":  [f1_result[-1][0], f1_result[-1][1]], "error_index": f1_result[-1][2]})
        return f1_result[-1][0], f1_result[-1][1], f1_result[-1][2]
        
    async def mrr(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        mrr_result = []
        for i in range(len(self.query)):
            temp = self.calculate_mrr(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k)
            # => send_dashboard()
            await self.sender_temp.send_dashboard(payload={"metric_name": "mrr", "score": temp.get("mrr")})

            temp = (temp.get("mrr"), temp.get("zero_rank_indexes"))
            print(f"-----[{i}] MRR RESULT: {temp} -----")
            mrr_result.append(temp)
            
        self.sender_temp.send_redis(payload={"metric_name": "mrr", "score":  mrr_result[-1][0], "error_index": mrr_result[-1][1]})    
        return mrr_result[-1][0], mrr_result[-1][1] # mrr_score, error_at_mrr_score
        
    
    async def context_relevance(self) -> Dict[str, float]:
        score = await context_relevance(
            llm=self.model,
            user_input=self.query,
            retrieved_contexts=self.predicted_docs
            )
        self.sender_temp.send_redis(payload={"metric_name": "context_relevance", "score": score})    
        return score
    
    async def map(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        map_result = []
        for i in range(len(self.query)):
            temp = self.calculate_map(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k)
            # => send_dashboard()
            await self.sender_temp.send_dashboard(payload={"metric_name": "map", "score": temp.get("map")})\

            temp = (temp.get("map"), temp.get("zero_score_indexes"))
            print(f"-----[{i}] MAP RESULT: {temp} -----")
            map_result.append(temp)

        self.sender_temp.send_redis(payload={"metric_name": "map", "score":  map_result[-1][0], "error_index": map_result[-1][1]})    
        return map_result[-1][0], map_result[-1][1]
    

    async def precision(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        precision_result = []
        for i in range(len(self.query)):
            temp = self.calculate_precision(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k)
            # => send_dashboard()
            await self.sender_temp.send_dashboard(payload={"metric_name": "precision", "score": [temp.get("micro_precision"), temp.get("macro_precision")]})

            temp = (temp.get("micro_precision"), temp.get("macro_precision"), temp.get("zero_score_indexes"))
            print(f"-----[{i}] PRECISION RESULT: {temp} -----")
            precision_result.append(temp)
        
        self.sender_temp.send_redis(payload={"metric_name": "precision", "score": [precision_result[-1][0], precision_result[-1][1]], "error_index": precision_result[-1][2]})    
        return precision_result[-1][0], precision_result[-1][1], precision_result[-1][2]
    
    async def recall(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        recall_result = []
        for i in range(len(self.query)):
            temp = self.calculate_recall(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k)
            # => send_dashboard()
            print("send dashboard: ",(temp.get("micro_recall"), temp.get("macro_recall")) )
            await self.sender_temp.send_dashboard(payload={"metric_name": "recall", "score": [temp.get("micro_recall"), temp.get("macro_recall")]})

            temp = (temp.get("micro_recall"), temp.get("macro_recall"), temp.get("zero_score_indexes"))
            print(f"-----[{i}] RECALL RESULT: {temp} -----")
            recall_result.append(temp)
        
        self.sender_temp.send_redis(payload={"metric_name": "recall", "score":  [recall_result[-1][0], recall_result[-1][1]], "error_index": recall_result[-1][2]})    
        return recall_result[-1][0], recall_result[-1][1], recall_result[-1][2]

    async def ndcg(self, k:int=5) -> Dict[str,float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        ndcg_result = []
        for i in range(len(self.query)):
            temp = self.calculate_ndcg(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k)
            # => send_dashboard()
            await self.sender_temp.send_dashboard(payload={"metric_name": "ndcg", "score": temp.get("ndcg")})

            temp = (temp.get("ndcg"), temp.get("zero_score_indexes"))
            print(f"-----[{i}] NDCG RESULT: {temp} -----")
            ndcg_result.append(temp)
    
        self.sender_temp.send_redis(payload={"metric_name": "ndcg", "score":  ndcg_result[-1][0], "error_index": ndcg_result[-1][1]})   
        return ndcg_result[-1][0], ndcg_result[-1][1]
