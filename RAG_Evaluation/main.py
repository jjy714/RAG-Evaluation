from fastapi import FastAPI, Request
from api.v1.endpoints.evaluator import evaluator
from api.v1.routers import api_router
from graphs.main_graph import create_main_graph, EvaluationState
from core.post_data import DataPointApiClient, DataPoint
from core.log_config import RedisSessionHandler
import logging
from typing import Any, Dict
from starlette.requests import Request as StarletteRequest
import json

app = FastAPI(
    title="RAG Evaluation API",
    description="An API to run RAG evaluation pipelines built with LangGraph.",
    version="1.0.0",
)
app.include_router(api_router, prefix="/v1")

# @TODO
"""
1. Create Logging sequence
Log as a file and store in User's -> session -> table in DB

2. Make the graph interaction individual to interact with the frontend. 

"""

@app.middleware("http") # 모든 http 요청에 대한 log
async def log_requests(request: Request, call_next):
    body_bytes = await request.body()
    if body_bytes:
        try:
            body = json.loads(body_bytes.decode("utf-8"))
        except json.JSONDecodeError:
            body = {}
    else:
        body = {}
    
    if "session_id" in body:
        session_id = body["session_id"]
        logger = logging.getLogger(f"session-{session_id}")
        logger.setLevel(logging.INFO)

        # 중복 핸들러 방지
        if not logger.handlers:
            logger.addHandler(RedisSessionHandler(session_id))

        logger.info("Called %s %s", request.method, request.url.path)
        
    # Body를 다시 request에 주입 (안 하면 endpoint에서 body 못 읽음)
    async def receive():
        return {"type": "http.request", "body": body_bytes}

    request = StarletteRequest(request.scope, receive)

    # 실제 endpoint 실행
    response = await call_next(request)
    return response


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok"}

###### 
@app.post("/send-datapoint")
async def send_datapoint(data: DataPoint):
    sender = DataPointApiClient(data.session_id, data.endpoint)
    return await sender.send_datapoint(data.payload)


@app.post("/eval_result") # 
async def get_eval_result(payload: Dict[str, Any]):
    print("payload:", payload)
    return {"eval_result": payload}