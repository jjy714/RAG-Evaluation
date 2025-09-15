from typing import List
from schema import EvaluationRequest
from langchain_core.documents import Document
from cache_redis import get_cache
from graphs import create_main_graph
from fastapi import APIRouter, HTTPException
from core import cleanse_data, create_input_payload
# import asyncio

## STEP 3. EVALUATE !!

router = APIRouter()

@router.post("/", status_code=202)
async def evaluator(evaluation_request: EvaluationRequest):
    graph_input = create_input_payload(evaluation_request)
    main_graph = create_main_graph()
    response = await main_graph.ainvoke(input=graph_input)
    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    print(retrieval_evaluation_result, generator_evaluation_result)
    return retrieval_evaluation_result, generator_evaluation_result

