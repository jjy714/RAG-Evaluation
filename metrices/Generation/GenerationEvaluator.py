from typing import Dict, List
from ragas.metrics import BleuScore
from ragas.metrics import RougeScore
from ragas.metrics._string import NonLLMStringSimilarity


class GenerationEvaluator:

    def __init__(self):
        pass


    async def string_similarity(self):
        """
        DOCUMENTATION

        The metric returns a score between 0 and 1, 
        where 1 indicates a perfect match between the response and the reference. 
        This is a non LLM based metric.
        """
        scorer = NonLLMStringSimilarity()
        await scorer.single_turn_ascore(sample)

    async def bleu(self):
        """
        DOCUMENTATION

        BLEU score ranges from 0 to 1, 
        where 1 indicates a perfect match between the response and the reference. 
        This is a non LLM based metric.
        """
        
        scorer = BleuScore()
        await scorer.single_turn_ascore(sample) 

    def rouge(self):
        """
        DOCUMENTATION
        
        You can change the rouge_type to rouge1 or rougeL 
        to calculate the ROUGE score based on unigrams or longest common subsequence respectively.
        
        You can change the mode to precision, recall, or fmeasure 
        to calculate the ROUGE score based on precision, recall, or F1 score respectively.
        
        """
        scorer = RougeScore(rouge_type="rouge1")
        scorer2 = RougeScore(mode="recall")
        
        pass

    def bert_score(self):
        pass
