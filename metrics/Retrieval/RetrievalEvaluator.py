from .MRR import map 
from .MRR import mrr
from .precision import precision, precision_at_k
from .recall import recall, recall_as_llm
from .noise_sensitivity import noise_sensitivity
from .response_relevancy import response_relevancy
# from .accuracy 


class RetrievalEvaluator:

    def __init__(self):
        self.metrics_list = [""]

        
    def mrr(self):
        return mrr(retrieved_docs="", ground_truth_ids="")
    
    def map(self):
        return 
    
    def precision(self):
        return
    
    def recall(self):
        return 
    
    def noise_sensitivity(self):
        return