from typing import List
from schema import EvaluationRequest
from langchain_core.documents import Document
from cache_redis import get_cache, set_cache
from graphs import create_main_graph
from fastapi.responses import JSONResponse
import json
from fastapi import APIRouter, HTTPException
from core import cleanse_data, create_input_payload
from core import RedisSessionHandler
import logging
# import asyncio

## STEP 3. EVALUATE !!

router = APIRouter()

@router.post("/", status_code=202)
async def evaluator(evaluation_request: EvaluationRequest):
    session_id = evaluation_request.session_id

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    redis_handler = RedisSessionHandler(session_id=session_id)
    logger.addHandler(redis_handler)


    graph_input = create_input_payload(evaluation_request)
    logger.info("Compiling Main Graph")

    main_graph = create_main_graph()
    response = await main_graph.ainvoke(input=graph_input)

    retrieval_evaluation_result = response.get("retriever_evaluation_result")
    generator_evaluation_result = response.get("generator_evaluation_result")
    logger.info(f"RETRIEVAL RESULT: {retrieval_evaluation_result},\nGENERATOR RESULT: {generator_evaluation_result}")

    # return JSONResponse(
    #         content={"status": "OK", "evaluate_result": {"retrieval_evaluation_result": retrieval_evaluation_result, "generator_evaluation_result": generator_evaluation_result}},
    #         status_code=200
    #     )
    # Redis Save On ##
    cache_input = {"retrieval_evaluation_result": retrieval_evaluation_result, "generator_evaluation_result": generator_evaluation_result}
    session_id = evaluation_request.session_id
    session_data = get_cache(session_id)
    session_data = json.loads(session_data)
    session_data["eval_result"] = cache_input
    set_cache(session_id, session_data)
    
    #### get again for locust test ### 
    eval_result = get_cache(session_id)
    eval_result = json.loads(eval_result)
    eval_result = eval_result["eval_result"]
    return JSONResponse(
        content={"status": "OK", "evaluate_result": {"retrieval_evaluation_result": eval_result['retrieval_evaluation_result'], "generator_evaluation_result": eval_result['generator_evaluation_result']}},
        status_code=200
    )

    #  retrieval_evaluation_result = {
    # "mrr": {"mrr_score": mrr_score, "error_at_mrr_score": error_at_mrr_score},
    # "map": {"map_score": map_score, "error_at_map_score": error_at_map_score},
    # "f1": {"f1_score": f1_score, "error_at_f1_score": error_at_f1_score},
    # "ndcg": {"ndcg_score": ndcg_score, "error_at_ndcg_score": error_at_ndcg_score},
    # "context_relevance": {"context_relevance_score": context_relevance_score, "error_at_context_relevance_score": error_at_context_relevance_score},
    # "precision": {"precision_score": precision_score, "error_at_precision_score": error_at_precision_score},
    # "recall": {"recall_score": recall_score, "error_at_recall_score": error_at_recall_score},
    # }