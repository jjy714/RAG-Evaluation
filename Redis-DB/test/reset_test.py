import redis

try:
    # Redis 서버에 연결
    r = redis.Redis(decode_responses=True)
    
    # 현재 데이터베이스의 모든 키를 삭제
    r.flushdb()
    
    print("현재 데이터베이스의 모든 데이터가 성공적으로 삭제되었습니다.")

except redis.exceptions.ConnectionError as e:
    print(f"Redis 연결에 실패했습니다: {e}")