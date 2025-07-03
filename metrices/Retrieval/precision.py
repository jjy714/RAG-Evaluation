
from ragas.metrics import NonLLMContextPrecisionWithReference
from ragas import SingleTurnSample, MultiTurnSample



async def precision():
    context_precision = NonLLMContextPrecisionWithReference()

    sample = SingleTurnSample(
        retrieved_contexts=["The Eiffel Tower is located in Paris."], 
        reference_contexts=["Paris is the capital of France.", "The Eiffel Tower is one of the most famous landmarks in Paris."]
    )

    await context_precision.single_turn_ascore(sample)


