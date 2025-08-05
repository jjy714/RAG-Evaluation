import redis
from fastapi import FastAPI

app = FastAPI()

# Docker Compose의 서비스 이름 'redis'를 host로 사용합니다.
# Docker 내부 네트워크가 알아서 해당 이름의 컨테이너로 연결해줍니다.
try:
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
    r.ping()
    print("성공적으로 Redis 컨테이너에 연결되었습니다.")
except redis.exceptions.ConnectionError as e:
    print(f"Redis 연결 실패: {e}")
    r = None

@app.post("/set/{key}/{value}")
def set_value(key: str, value: str):
    if r:
        r.set(key, value)
        return {"message": f"'{key}'에 '{value}'를 저장했습니다."}
    return {"error": "Redis에 연결되지 않았습니다."}, 500

@app.get("/get/{key}")
def get_value(key: str):
    if r:
        value = r.get(key)
        if value is None:
            return {"error": f"'{key}'를 찾을 수 없습니다."}, 404
        return {key: value}
    return {"error": "Redis에 연결되지 않았습니다."}, 500