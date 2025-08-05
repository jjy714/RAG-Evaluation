import redis

# Redis 서버에 연결 (기본 설정: host='localhost', port=6379, db=0)
try:
    r = redis.Redis(decode_responses=True)
    # decode_responses=True 로 설정하면 Redis에서 가져온 데이터를 자동으로 UTF-8로 디코딩해줍니다.
    # 이렇게 하면 b'value' 대신 'value' 형태로 값을 받을 수 있어 편리합니다.

    # 서버에 연결되었는지 확인
    r.ping()
    print("Redis에 성공적으로 연결되었습니다!")

except redis.exceptions.ConnectionError as e:
    print(f"Redis 연결에 실패했습니다: {e}")