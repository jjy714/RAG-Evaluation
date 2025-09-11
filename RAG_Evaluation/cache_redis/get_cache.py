import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_PORT = os.getenv("REDIS_PORT")


def get_cache(session_id):
    r = redis.Redis(
        host='localhost',
        port=int(REDIS_PORT),
        decode_responses=True
        )
    try:
        r.ping()
        print("Connected to Redis!")
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")

    # Example: Set and get a value
    return_value = r.get(session_id)
    print(f"Value of {session_id}: {return_value}")
    return return_value
    