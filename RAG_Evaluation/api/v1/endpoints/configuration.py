from fastapi import APIRouter
from pathlib import Path
from pydantic import BaseModel
from SHARED_PROCESS import SHARED_PROCESS
from schema import UserConfig
import uuid

router = APIRouter()

data_path = str(Path(".").resolve())


## STEP 1. CONFIG FIRST !!


@router.post("/config")
async def store_config(config: UserConfig):
    session_id = str(uuid.uuid4())
    SHARED_PROCESS[session_id]["config"] = config     
    
    return {"session_id": session_id, "message": "Session Configuration set successfully."}




