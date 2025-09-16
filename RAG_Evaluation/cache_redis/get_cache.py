import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_HOST = os.getenv("REDIS_HOST")

def get_cache(session_id):
    r = redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        decode_responses=True
        )
    try:
        r.ping()
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")

    # Example: Set and get a value
    return_value = r.get(session_id)
    return return_value
    