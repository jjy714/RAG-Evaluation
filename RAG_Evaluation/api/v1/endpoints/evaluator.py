from typing import List
from schema import EvaluationRequest
from langchain_core.documents import Document
from cache_redis import get_cache, set_cache
from graphs import create_main_graph
from fastapi.responses import JSONResponse
import json
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
    # print(retrieval_evaluation_result, generator_evaluation_result)
    return JSONResponse(
            content={"status": "OK", "evaluate_result": {"retrieval_evaluation_result": retrieval_evaluation_result, "generator_evaluation_result": generator_evaluation_result}},
            status_code=200
        )
    # # Redis Save On ##
    # cache_input = {"retrieval_evaluation_result": retrieval_evaluation_result, "generator_evaluation_result": generator_evaluation_result}
    # session_id = evaluation_request.session_id
    # session_data = get_cache(session_id)
    # session_data = json.loads(session_data)
    # session_data["eval_result"] = cache_input
    # set_cache(session_id, session_data)
    # #### get again ### 
    # eval_result = get_cache(session_id)
    # eval_result = json.loads(eval_result)
    # eval_result = eval_result["eval_result"]
    # return JSONResponse(
    #     content={"status": "OK", "evaluate_result": {"retrieval_evaluation_result": eval_result['retrieval_evaluation_result'], "generator_evaluation_result": eval_result['generator_evaluation_result']}},
    #     status_code=200
    # )
