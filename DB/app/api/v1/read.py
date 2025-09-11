from core import read_data
from fastapi import APIRouter, HTTPException, UploadFile, File
from concurrent.futures import ThreadPoolExecutor
import traceback
import time
import asyncio

router = APIRouter()

@router.get("/find/mongo/{file_name}")
async def read_from_mongo(file_name: str):
    executor = ThreadPoolExecutor(max_workers=10)
    try:
        loop = asyncio.get_running_loop()

        record_count = await loop.run_in_executor(
            executor, read_data, int(time.time()),file_name
        )

        return {"message": f"Successfully read {file_name} with {record_count} records from MongoDB."}

    except Exception as e:
        print("ERROR during read_from_mongo:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
