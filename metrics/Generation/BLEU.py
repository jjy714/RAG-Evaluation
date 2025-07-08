from ragas.metrics import BleuScore
from ragas import SingleTurnSample
import numpy as np
from typing import List

from ragas.dataset_schema import SingleTurnSample 
from typing import List, Dict
import numpy as np


async def bleu(response: List, reference:List) -> Dict[str, float]:
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
    ) for res, doc in zip(response, reference)]

    for i in data_list:
        result = await scorer.single_turn_ascore(i)
    result = np.mean(result)
    return {"BLEU": result}