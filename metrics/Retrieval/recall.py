from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import LLMContextRecall
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import NonLLMContextRecall

async def recall_as_llm():
    sample = SingleTurnSample(
        user_input="Where is the Eiffel Tower located?",
        response="The Eiffel Tower is located in Paris.",
        reference="The Eiffel Tower is located in Paris.",
        retrieved_contexts=["Paris is the capital of France."], 
    )

    context_recall = LLMContextRecall(llm=evaluator_llm)
    await context_recall.single_turn_ascore(sample)



async def recall(retrieved_contexts, reference_contexts):
    sample = SingleTurnSample(
        retrieved_contexts=["Paris is the capital of France."], 
        reference_contexts=["Paris is the capital of France.", "The Eiffel Tower is one of the most famous landmarks in Paris."]
    )

    context_recall = NonLLMContextRecall()
    return await context_recall.single_turn_ascore(sample)
