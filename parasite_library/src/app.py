
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from typing import Dict
from parasite_library.DataProcessor.DataPreprocessor import data_process
from parasite_library.GenerateReport.GenerateReport import generate_report

app = FastAPI() 

"""
@TODO

Need to create a REQUEST & RESPONSE mechanism 

1. create endpoints.
2. create prompts

Test the basic prototype


"""

@app.post("/")
def main():
    yield {"status": 200}
    

@app.post("/data")
async def receieve_data(file: UploadFile = File(...)):
    content: bytes = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    print("Uploaded file name:", file.filename)
    preprocessed_data = await data_process(content)

    
    return {"status": "ok", "data": preprocessed_data}

@app.post("/get-evaluate-report")
async def get_evaluate_report(payload : Dict):
    session_id = payload["session_id"]

    return {"eval_report": await generate_report(session_id=session_id)}


# 임시. UI가 없어서 성능 포인트 전달 확인하기 위함. core.evaluator에서 엔드포인트 수정
@app.post("/get-metric-score")
async def get_datapoint(request: Request):
    datapoint = await request.json()

    print("datapoint JSON:", datapoint)
    return {"status": "ok", "received": datapoint}

    #uv run uvicorn app:app --reload --host 0.0.0.0 --port 8005