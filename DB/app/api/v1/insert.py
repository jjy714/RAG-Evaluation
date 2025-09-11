from fastapi import APIRouter, HTTPException, UploadFile, File
from concurrent.futures import ThreadPoolExecutor
from core import insert_data
import traceback
import time
import asyncio

router = APIRouter()

@router.post("/upload/mongo")
async def upload_to_mongo(file: UploadFile = File(...)):
    executor = ThreadPoolExecutor(max_workers=10)
    
    print(file)
    try:
        contents = await file.read()
        loop = asyncio.get_running_loop()
        
        record_count = await loop.run_in_executor(
            executor, insert_data, int(time.time()), file.filename, contents
        )

        return {"message": f"Successfully uploaded {file.filename} with {record_count} records to MongoDB."}

    except Exception as e:
        print("ERROR during upload_to_mongo:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))