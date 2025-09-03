from typing import Annotated
import requests
import httpx
from fastapi import APIRouter, File, UploadFile
import aiofiles
from pathlib import Path
from data import DataPreprocessor

router = APIRouter()

data_path = str(Path(".").resolve())

preprocessor = DataPreprocessor()

@router.post("/dataset-create")
async def write_file(file: UploadFile):
    print(data_path)
    async with aiofiles.open(f"{data_path}/test/{file.filename}", 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    
    return {"status": f"{file.filename}"}


@router.post("/dataset-create/custom")
async def write_file(per_data: str):
    """
    Sends to LLM
    Sends to VDB
    """
    response = await requests.post()
    
    return {"status": f"{file.filename}"}

@router.get("/from-main-db")
async def get_file_from_main_db(file: Annotated[bytes, File()]):
    
    response = requests.get("https://google.com")
    return {"status": f"{file.title} !!"}




@router.post("/upload-dataset")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}