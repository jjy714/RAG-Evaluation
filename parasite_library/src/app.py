
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Dict
from parasite_library.DataProcessor.DataPreprocessor import data_process
from parasite_library.GenerateReport.GenerateReport import main

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
# src
#  uv run uvicorn app:app --reload --port 8001

@app.post("/get-evaluate-report")
async def get_evaluate_report(payload : Dict):
    session_id = payload["session_id"]

    return {"eval_report": await main(session_id=session_id)}