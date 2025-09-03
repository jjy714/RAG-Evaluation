from typing import Annotated
import requests
from fastapi import APIRouter, File, UploadFile
import json
import aiofiles
from pathlib import Path
router = APIRouter()

data_path = str(Path(".").resolve())

@router.post("/logs")
async def receieve_logs(logs):
    print(data_path)
    return {"status": f"{file.filename}"}
