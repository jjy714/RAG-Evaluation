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


# from .accuracy 
class ApiClient:
    def __init__(self, session_id: str, endpoint: str):
        self.endpoint = endpoint
        self.session_id = session_id
        print(f"API Client initialized for endpoint: {self.endpoint}")
        
        
    def send_redis(self, data, error): 
        return set_cache(session_id=self.session_id, input=(data, error))

    async def send_dashboard(self, payload: Dict[str, Any]):
        """Sends a single metric data point to the dashboard API."""
        async with httpx.AsyncClient() as client:    
            try:
                response = client.post(self.endpoint, json=payload)
                response.raise_for_status()
                print(f"Successfully sent metric: {payload['metric_name']}")
            except client.RequestException as e:
                print(f"Error sending metric to dashboard: {e}")
        return response


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
        
        self.sender = ApiClient(session_id=session_id, endpoint=endpoint)
        
        
        self.query = query
        self.model = model
        self.predicted_docs = predicted_documents
        
        self.actual_docs = ground_truth_documents
        self.predicted_docs = predicted_documents
        
        
    def f1(self, k:int=5) -> List[Dict[str, float]]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        f1_result = []
        for i in range(len(self.query)):
            temp = (self.calculate_f1_score(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("micro_f1"), self.calculate_f1_score(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("macro_f1"))
            print(f"-----[{i}] F1 RESULT: {temp} -----")
            self.sender.send_redis()
            f1_result.append(temp)
        # f1 _result = [f1 score list , error index list]
        return f1_result[0][-1], f1_result[-1]
        
    def mrr(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        mrr_result = []
        for i in range(len(self.query)):
            temp = self.calculate_mrr(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("mrr")
            print(f"-----[{i}] MRR RESULT: {temp} -----")
            mrr_result.append(temp)
            
            
        return mrr_result[0][-1], mrr_result[-1]
        
    
    async def context_relevance(self) -> Dict[str, float]:
        return await context_relevance(
            llm=self.model,
            user_input=self.query,
            retrieved_contexts=self.predicted_docs
            )
    
    def map(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        map_result = []
        for i in range(len(self.query)):
            temp = self.calculate_map(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("map")
            print(f"-----[{i}] MAP RESULT: {temp} -----")
            map_result.append(temp)
        
        return map_result[0][-1], map_result[-1]
    
    def precision(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        precision_result = []
        for i in range(len(self.query)):
            temp = (self.calculate_precision(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("micro_f1"), self.calculate_precision(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i],k=k).get("macro_f1"))
            print(f"-----[{i}] PRECISION RESULT: {temp} -----")
            precision_result.append(temp)
        
        return precision_result[0][-1], precision_result[-1]
    
    def recall(self, k:int=5) -> Dict[str, float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        recall_result = []
        for i in range(len(self.query)):
            temp = (self.calculate_recall(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("micro_f1"), self.calculate_recall(k=k).get("macro_f1"))
            print(f"-----[{i}] RECALL RESULT: {temp} -----")
            recall_result.append(temp)
        
        return recall_result[0][-1], recall_result[-1]
    
    def ndcg(self, k:int=5) -> Dict[str,float]:
        actual_doc = self.actual_docs
        predicted_doc = self.predicted_docs
        
        ndcg_result = []
        for i in range(len(self.query)):
            temp = (self.calculate_ndcg(actual_docs=actual_doc[:i], predicted_docs=predicted_doc[:i], k=k).get("ndcg"))
            print(f"-----[{i}] NDCG RESULT: {temp} -----")
            ndcg_result.append(temp)
        
        return ndcg_result[0][-1], ndcg_result[-1]
