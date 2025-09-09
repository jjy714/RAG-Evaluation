
from fastapi import FastAPI, UploadFile, File, HTTPException
import json
from parasite_library.DataProcessor.DataPreprocessor import data_process
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
# uvicorn app:app --reload --port 8000