import redis
import os
from dotenv import load_dotenv
from pathlib import Path
import json
# env_path = Path('.').parent.resolve()
# print(env_path)
load_dotenv()

REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_HOST = os.getenv("REDIS_HOST")

print(REDIS_PORT)


def set_cache(session_id, input):
    
    
    if not (
        isinstance(input, bytes) or
        isinstance(input, str) or
        isinstance(input, int) or
        isinstance(input, float)):
        input = json.dumps(input)
    
    r = redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        decode_responses=True
    )
    try:
        r.ping()
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
    try: 
        r.set(session_id, input)
    except Exception as e:
        print(e)
