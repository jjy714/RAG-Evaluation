from ragas import SingleTurnSample 
from ragas.metrics import ResponseRelevancy

async def response_relevancy():
    sample = SingleTurnSample(
        user_input="When was the first super bowl?",
        response="The first superbowl was held on Jan 15, 1967",
        retrieved_contexts=[
            "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
        ]
    )

    scorer = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
    await scorer.single_turn_ascore(sample)





    