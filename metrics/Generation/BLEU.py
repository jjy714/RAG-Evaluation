from ragas.metrics import BleuScore
from ragas import SingleTurnSample
import numpy as np
from typing import List



def bleu(response: List, retrieved_documents:List):
    """
    DOCUMENTATION

    BLEU score ranges from 0 to 1, 
    where 1 indicates a perfect match between the response and the reference. 
    This is a non LLM based metric.
    """
    scorer = BleuScore()
    data_list = [SingleTurnSample(
        response=res,
        reference=doc
    ) for res, doc in zip(response, retrieved_documents)]
    result = [scorer.single_turn_ascore(i) for i in data_list]
    result = np.mean(result)
    return result