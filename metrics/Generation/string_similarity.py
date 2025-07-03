from ragas.metrics._string import NonLLMStringSimilarity


async def string_similarity(self):
    """
    DOCUMENTATION

    The metric returns a score between 0 and 1, 
    where 1 indicates a perfect match between the response and the reference. 
    This is a non LLM based metric.
    """
    scorer = NonLLMStringSimilarity()
    await scorer.single_turn_ascore(sample)