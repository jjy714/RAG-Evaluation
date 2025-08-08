from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import ContextRelevance
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from typing import List, Dict

async def context_relevance(llm: ChatOpenAI | AzureChatOpenAI, user_input: List, response: List, retrieved_contexts: List[str | List]) -> Dict[str, float]:
    evaluator_llm = LangchainLLMWrapper(llm)
    sample = SingleTurnSample(
        user_input="When and Where Albert Einstein was born?",
        retrieved_contexts=[
            "Albert Einstein was born March 14, 1879.",
            "Albert Einstein was born at Ulm, in Württemberg, Germany.",
        ]
    )

    scorer = ContextRelevance(llm=evaluator_llm)
    score = await scorer.single_turn_ascore(sample)
    return score
