import json
from typing import Any, Dict
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from cache_redis import get_cache, set_cache
from pydantic import BaseModel


class DataPoint(BaseModel):
    session_id: str
    endpoint: str
    payload: Dict[str, Any]  


    #  retrieval_evaluation_result = {
    # "mrr": {"mrr_score": mrr_score, "error_at_mrr_score": error_at_mrr_score},
    # "map": {"map_score": map_score, "error_at_map_score": error_at_map_score},
    # "f1": {"f1_score": f1_score, "error_at_f1_score": error_at_f1_score},
    # "ndcg": {"ndcg_score": ndcg_score, "error_at_ndcg_score": error_at_ndcg_score},
    # "context_relevance": {"context_relevance_score": context_relevance_score, "error_at_context_relevance_score": error_at_context_relevance_score},
    # "precision": {"precision_score": precision_score, "error_at_precision_score": error_at_precision_score},
    # "recall": {"recall_score": recall_score, "error_at_recall_score": error_at_recall_score},
    # }

class DataPointApiClient:
    def __init__(self, session_id: str, endpoint: str):
        self.endpoint = endpoint
        self.session_id = session_id
        print(f"API Client initialized for endpoint: {self.endpoint}")

    def send_redis(self, payload: Dict[str, Any]):
        session_data = get_cache(session_id=self.session_id)
        if isinstance(session_data, str):
            session_data = json.loads(session_data)
        
        session_data["metric_name"] = payload["metric_name"]
        if "metric_result" not in session_data:
            session_data["metric_result"] = {}

        if payload["metric_name"] not in session_data["metric_result"]:
            session_data["metric_result"][payload["metric_name"]] = {}
            
        session_data["metric_result"][payload["metric_name"]]["score"] = payload["score"]
        session_data["metric_result"][payload["metric_name"]]["error_index"] = payload["error_index"]

        return set_cache(session_id=self.session_id, input=session_data)

    async def send_dashboard(self, payload: Dict[str, Any]):
        # ui endpoint로 데이터 post
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.endpoint, json=payload) # payload = {"metric_name": str, "score": int}
                response.raise_for_status()
                print(f"Successfully sent metric: {payload['metric_name']}")
                return response.json()
            except httpx.RequestError as e:
                print(f"Error sending metric to dashboard: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def send_datapoint(self, payload):
        try:
        
            # metric 거쳐서 나온 score list & error list
            metric_name = payload['metric_name']
            score_result = payload["score"]
            error_list = payload["error_list"]


            payload = {"metric_name" : metric_name, "score": score_result, "error_index": error_list}

            self.send_redis(payload=payload)

            for point in score_result: # goekd score list를 for문으로 풀어 UI에 전달
                result = await self.send_dashboard({"metric_name": metric_name, "score":point})

                return {"status": "success", "response": result}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
