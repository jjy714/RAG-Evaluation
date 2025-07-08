from ragas.metrics import RougeScore
from ragas import SingleTurnSample
from typing import List, Dict
import numpy as np


async def rouge(
        response: List,
        reference: List,
        rouge_type: str | None = "rouge1", 
        mode: str | None = "recall",
        )-> Dict[str, float]:
    """
    DOCUMENTATION
    
    You can change the rouge_type to rouge1 or rougeL 
    to calculate the ROUGE score based on unigrams or longest common subsequence respectively.
    
    You can change the mode to precision, recall, or fmeasure 
    to calculate the ROUGE score based on precision, recall, or F1 score respectively.
    
    """
    scorer = RougeScore(rouge_type=rouge_type)

    data_list = [SingleTurnSample(
        response=res,
        reference=doc
    ) for res, doc in zip(response, reference)]

    for i in data_list:
        result = await scorer.single_turn_ascore(i)
    result = np.mean(result)
    return {"ROUGE": result}