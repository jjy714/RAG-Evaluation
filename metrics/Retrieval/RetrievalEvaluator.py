from MAP import map 
from MRR import mrr
from precision import precision, precision_at_k
from recall import recall, recall_as_llm


class RetrievalEvaluator:

    def __init__(
            self,
            metrics,
            dataset,
            ):
        
        self.metrics = metrics
        self.dataset = dataset
        
    def mrr(self):
        return mrr(retrieved_docs="", ground_truth_ids="")
    
    def map(self):
        return 
    
    def precision(self):
        return
    
    def recall(self):
        return 
    
    