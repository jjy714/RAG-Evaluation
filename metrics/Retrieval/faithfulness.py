from ragas.dataset_schema import SingleTurnSample 
from ragas.metrics import Faithfulness

async def faithfulness():
    sample = SingleTurnSample(
            user_input="When was the first super bowl?",
            response="The first superbowl was held on Jan 15, 1967",
            retrieved_contexts=[
                "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
            ]
        )
    scorer = Faithfulness(llm=evaluator_llm)
    await scorer.single_turn_ascore(sample)