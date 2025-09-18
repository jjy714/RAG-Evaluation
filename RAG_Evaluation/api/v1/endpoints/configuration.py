from fastapi import APIRouter
from schema import UserConfig
from cache_redis import set_cache
from core import RedisSessionHandler
import logging
import uuid
import json

router = APIRouter()


## STEP 1. CONFIG FIRST !!


@router.post("")
def store_config(config: UserConfig):
    
    
    session_id = str(uuid.uuid4())
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    redis_handler = RedisSessionHandler(session_id=session_id)
    logger.addHandler(redis_handler)
    
    logger.info(f"RECIEVED CONFIG {config}")
    logger.debug(f"Dumping to UserConfig {config}")
    json_config = UserConfig.model_dump(config)
    
    logger.debug(f"Dumping as json {config}")
    json_config = json.dumps(json_config)
    
    session_data = {
        "config": json_config, # Store config as a dictionary
        "benchmark_dataset": None,      # Add a placeholder for the dataset
        "session_log": []
    }
    try:
        set_cache(session_id=session_id, input=session_data)
        logger.info(f" SESSION ID {session_id} stored success !")
    except:
        logger.error(f" [api/v1/endpoints/configuration.py] ERROR setting session data")
    return {"session_id": session_id, "message": "Session Configuration set successfully."}
