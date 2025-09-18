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



class DataPointApiClient:
    def __init__(self, session_id: str, endpoint: str):
        self.endpoint = endpoint
        self.session_id = session_id
        print(f"API Client initialized for endpoint: {self.endpoint}")

    def send_redis(self, data: Dict[str, Any], error: [str]):
        session_data = get_cache(session_id=self.session_id)
        if isinstance(session_data, str):
            session_data = json.loads(session_data)
        
        session_data["metric_name"] = data["metric_name"]
        if "metric_result" not in session_data:
            session_data["metric_result"] = {}

        if data["metric_name"] not in session_data["metric_result"]:
            session_data["metric_result"][data["metric_name"]] = {}
            
        session_data["metric_result"][data["metric_name"]]["score"] = data["metric_score"] ##
        session_data["metric_result"][data["metric_name"]]["error_index"] = error

        return set_cache(session_id=self.session_id, input=session_data)

    async def send_dashboard(self, payload: Dict[str, Any]):
        # ui endpoint로 데이터 post
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.endpoint, json=payload)
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
            score_result = payload["eval_result"][metric_name][0]
            error_list = payload["eval_result"][metric_name][1]


            payload = {"metric_name" : metric_name, "metric_score": score_result}

            self.send_redis(data=payload, error=error_list)

            for point in score_result: # goekd score list를 for문으로 풀어 UI에 전달
                result = await self.send_dashboard({"metric_name": metric_name, "score":point})

                return {"status": "success", "response": result}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
