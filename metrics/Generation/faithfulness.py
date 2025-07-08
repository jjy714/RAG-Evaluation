from ragas.dataset_schema import SingleTurnSample 
from ragas.metrics import Faithfulness
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI, AzureChatOpenAI

from typing import List, Dict
import numpy as np

    # SingleTurnSample(user_input=q, response=a, retrieved_contexts=r)

async def faithfulness(llm: ChatOpenAI | AzureChatOpenAI, user_input: List, response: List, retrieved_contexts: List) -> Dict[str, float]:
    evaluator_llm = LangchainLLMWrapper(llm)
    scorer = Faithfulness(llm=evaluator_llm)
    
    data_list = []
    results=[]
    for user_input, response, retrieved_contexts in zip(user_input, response, retrieved_contexts):
        data_list.append(
            SingleTurnSample(user_input=user_input, response=response, retrieved_contexts=retrieved_contexts)
            )

    for i in data_list:
        temp = await scorer.single_turn_ascore(i)
        results.append(temp)

    print(f"FAITHFULNESS MODULE {results}")
    if not results:
        result = 0.0

    result = np.mean(results)
    return result