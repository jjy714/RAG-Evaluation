from ragas.metrics import BleuScore



async def bleu(self):
    """
    DOCUMENTATION

    BLEU score ranges from 0 to 1, 
    where 1 indicates a perfect match between the response and the reference. 
    This is a non LLM based metric.
    """
    
    scorer = BleuScore()
    await scorer.single_turn_ascore(sample) 