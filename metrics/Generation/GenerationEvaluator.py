from typing import Dict, List
from BLEU import bleu
from ROUGE import rouge
from string_similarity import string_similarity
from BertScore import bert_score

class GenerationEvaluator:

    def __init__(
            self,
            dataset, 
            metrics
            ):
        
        self.dataset = dataset
        self.metrics = metrics



    def bleu(self):
        pass

    def rouge(self):
        pass

    def string_similarity(self):
        pass

    def bert_score(self):
        pass