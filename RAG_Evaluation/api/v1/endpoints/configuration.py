from fastapi import APIRouter
from schema import UserConfig
from cache_redis import set_cache
import uuid
import json

router = APIRouter()


## STEP 1. CONFIG FIRST !!


@router.post("")
def store_config(config: UserConfig):
    print(config)
    session_id = str(uuid.uuid4())

    json_config = UserConfig.model_dump(config)
    json_config = json.dumps(json_config)
    
    session_data = {
        "config": json_config, # Store config as a dictionary
        "benchmark_dataset": None      # Add a placeholder for the dataset
    }
    
    set_cache(session_id=session_id, input=session_data)
    return {"session_id": session_id, "message": "Session Configuration set successfully."}
