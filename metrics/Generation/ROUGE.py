from ragas.metrics import RougeScore
from ragas import SingleTurnSample
from typing import List 
import numpy as np


async def rouge(
        self, 
        response: List,
        retrieved_documents: List,
        rouge_type: str = "rouge1", 
        mode: str = "recall",
        ):
    """
    DOCUMENTATION
    
    You can change the rouge_type to rouge1 or rougeL 
    to calculate the ROUGE score based on unigrams or longest common subsequence respectively.
    
    You can change the mode to precision, recall, or fmeasure 
    to calculate the ROUGE score based on precision, recall, or F1 score respectively.
    
    """
    scorer = RougeScore(rouge_type=rouge_type)
    scorer2 = RougeScore(mode=mode)

    data_list = [SingleTurnSample(
        response=res,
        reference=doc
    ) for res, doc in zip(response, retrieved_documents)]
    result = [scorer.single_turn_ascore(i) for i in data_list]
    result = np.mean(result)
    await result