from typing import Annotated
import requests
from fastapi import APIRouter, File, UploadFile
import json
import aiofiles
from pathlib import Path
router = APIRouter()

data_path = str(Path(".").resolve())

@router.post("/create-config")
async def write_config_file(file: json):
    print(data_path)
    
    
    async with aiofiles.open(f"{data_path}/test/{file.filename}", 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    
    return {"status": f"{file.filename}"}

@router.post("/upload-dataset")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}