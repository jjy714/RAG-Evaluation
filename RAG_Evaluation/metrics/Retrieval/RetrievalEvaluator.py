from langchain_core.documents  import Document
from krag.evaluators import OfflineRetrievalEvaluators
from .context_relevance import context_relevance
from langchain_openai import ChatOpenAI, AzureChatOpenAI
# from .MRR import map 
# from .MRR import mrr
# from .precision import precision, precision_at_k
# from .recall import recall, recall_as_llm
# from .noise_sensitivity import noise_sensitivity
# from .response_relevancy import response_relevancy
from typing import Union, List, Dict, Optional
from enum import Enum
import asyncio


# from .accuracy 


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
            user_input: List[str],
            actual_docs: List[List[Document]], 
            predicted_docs: List[List[Document]],
            model: ChatOpenAI | AzureChatOpenAI,
            match_method: str = "text", 
            averaging_method: Union[str, AveragingMethod] = AveragingMethod.BOTH,
            matching_criteria: MatchingCriteria = MatchingCriteria.ALL
            ):
        super().__init__(
            actual_docs, 
            predicted_docs, 
            match_method, 
            averaging_method, 
            matching_criteria
        )
        self.user_input = user_input
        self.model = model
        self.predicted_docs = predicted_docs
        
    def f1(self, k:int=5) -> Dict[str, float]:
        return self.calculate_f1_score(k=k).get("micro_f1"), self.calculate_f1_score(k=k).get("macro_f1")
            
    def mrr(self, k:int=5) -> Dict[str, float]:
        return self.calculate_mrr(k=k).get("mrr")
    
    async def context_relevance(self) -> Dict[str, float]:
        return await context_relevance(
            llm=self.model,
            user_input=self.user_input,
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

