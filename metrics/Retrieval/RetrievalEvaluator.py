from langchain_core.documents  import Document
from krag.evaluators import OfflineRetrievalEvaluators


# from .MRR import map 
# from .MRR import mrr
# from .precision import precision, precision_at_k
# from .recall import recall, recall_as_llm
# from .noise_sensitivity import noise_sensitivity
# from .response_relevancy import response_relevancy
from typing import Union, List, Dict, Optional
from enum import Enum


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
            actual_docs: List[List[Document]], 
            predicted_docs: List[List[Document]], 
            match_method: str = "text", 
            averaging_method: AveragingMethod = AveragingMethod.BOTH, 
            matching_criteria: MatchingCriteria = MatchingCriteria.ALL
            ):
        super().__init__(
            actual_docs, 
            predicted_docs, 
            match_method, 
            averaging_method, 
            matching_criteria
            )
        self.metrics_list = [""]

        
    def f1(self, k:int=5) -> Dict[str, float]:
        return self.calculate_f1_score(k=k).get("f1")
    def mrr(self, k:int=5) -> Dict[str, float]:
        return self.calculate_mrr(k=k).get("mrr")
    
    def map(self, k:int=5) -> Dict[str, float]:
        return self.calculate_map(k=k).get("map")
    
    def precision(self, k:int=5) -> Dict[str, float]:
        return self.calculate_precision(k=k).get("precision")
    
    def recall(self, k:int=5) -> Dict[str, float]:
        return self.calculate_recall(k=k).get("recall")
    
    def ndcg(self, k:int=5) -> Dict[str,float]:
        return self.calculate_ndcg(k=k).get("ndcg")

