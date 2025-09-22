
from fastapi import FastAPI, UploadFile, File, HTTPException
import json
from typing import List, Dict, Any
import polars as pl
from parasite_library.DataProcessor.DataPreprocessor import data_process
from parasite_library.GenerateReport.GenerateReport import main
from pydantic import BaseModel, field_validator

app = FastAPI() 

class GenerateEvalReport(BaseModel):
    session_id : str
    data : List[Dict[str, Any]]
    @field_validator("data", mode="after")
    def convert_to_pl(cls, v):
        return pl.DataFrame(v)


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
async def get_evaluate_report(payload : GenerateEvalReport):
    session_id = payload.session_id
    data = payload.data

    return {"eval_report": await main(session_id=session_id, data=data)}