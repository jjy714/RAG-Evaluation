from langchain_core.documents  import Document
from ..krag.evaluators import OfflineRetrievalEvaluators
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
import httpx
import asyncio


# from .accuracy 
class ApiClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        # You might use a requests.Session() here for connection pooling
        print(f"API Client initialized for endpoint: {self.endpoint}")

    async def send_metric(self, payload: Dict[str, Any]):
        """Sends a single metric data point to the dashboard API."""
        # In a real implementation, you would use a library like requests or httpx
        async with httpx.AsyncClient() as client:    
            try:
                response = client.post(self.endpoint, json=payload)
                response.raise_for_status() # Raise an exception for bad status codes
                print(f"Successfully sent metric: {payload['metric_name']}")
            except client.RequestException as e:
                print(f"Error sending metric to dashboard: {e}")
        print(f"[API Call Simulation] Sending payload: {payload}")


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
            match_method: str = "text", 
            averaging_method: Union[str, AveragingMethod] = AveragingMethod.BOTH,
            matching_criteria: MatchingCriteria = MatchingCriteria.ALL
            ):
        super().__init__(
            actual_docs=ground_truth_documents, 
            predicted_docs=predicted_documents, 
            match_method= match_method, 
            averaging_method=averaging_method, 
            matching_criteria=matching_criteria
        )
        self.query = query
        self.model = model
        self.predicted_docs = predicted_documents
        
    def f1(self, k:int=5) -> Dict[str, float]:
        return self.calculate_f1_score(k=k).get("micro_f1"), self.calculate_f1_score(k=k).get("macro_f1")
            
    def mrr(self, k:int=5) -> Dict[str, float]:
        return self.calculate_mrr(k=k).get("mrr")
    
    async def context_relevance(self) -> Dict[str, float]:
        return await context_relevance(
            llm=self.model,
            user_input=self.query,
            retrieved_contexts=self.predicted_docs
            )
    
    def map(self, k:int=5) -> Dict[str, float]:
        
        return self.calculate_map(k=k).get("map")
    
    def precision(self, k:int=5) -> Dict[str, float]:
        return self.calculate_precision(k=k).get("micro_precision"), self.calculate_precision(k=k).get("macro_precision")
    
    def recall(self, k:int=5) -> Dict[str, float]:
        return self.calculate_recall(k=k).get("micro_recall"), self.calculate_recall(k=k).get("macro_recall")
    
    def ndcg(self, k:int=5) -> Dict[str,float]:
        return self.calculate_ndcg(k=k).get("ndcg")

