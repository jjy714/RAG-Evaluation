from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import AnswerAccuracy
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from typing import List, Dict


async def answer_accuracy(llm: ChatOpenAI | AzureChatOpenAI, user_input: List, response: List, retrieved_contexts: List[str | List]) -> Dict[str, float]:
    evaluator_llm = LangchainLLMWrapper(llm)
    sample = SingleTurnSample(
        user_input="When was Einstein born?",
        response="Albert Einstein was born in 1879.",
        reference="Albert Einstein was born in 1879."
    )

    scorer = AnswerAccuracy(llm=evaluator_llm) # evaluator_llm wrapped with ragas LLM Wrapper
    score = await scorer.single_turn_ascore(sample)
    return score