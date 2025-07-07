from typing import Dict, List
from BLEU import bleu
from ROUGE import rouge
from string_similarity import string_similarity
from BertScore import bert_score
from langchain_core.documents import Document


class GenerationEvaluator:

    def __init__(
            self,
            actual_docs: List[List[Document]], 
            predicted_docs: List[List[Document]], 
            ):
        
        self.actual_docs = actual_docs
        self.predicted_docs = predicted_docs


    def bleu(self):
        pass

    def rouge(self):
        pass

    def string_similarity(self):
        pass

    def bert_score(self):
        pass