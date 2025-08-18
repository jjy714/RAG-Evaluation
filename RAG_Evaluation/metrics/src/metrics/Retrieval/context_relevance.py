from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import ContextRelevance
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.documents import Document
from tqdm import tqdm
import numpy as np
from typing import List, Dict


async def context_relevance(llm: ChatOpenAI | AzureChatOpenAI, user_input: List, retrieved_contexts: List[List[Document]]) -> Dict[str, float]:
    evaluator_llm = LangchainLLMWrapper(llm)
    scorer = ContextRelevance(llm=evaluator_llm)
    results = []
    
    data_list = [SingleTurnSample(
        response=res,
        reference=[i.page_content for i in doc]
    ) for res, doc in zip(user_input, retrieved_contexts)]

    for i in tqdm(data_list):
        temp = await scorer.single_turn_ascore(i)
        results.append(temp)
    if not results:
        result = 0.0
    result = np.mean(results)
    return result

