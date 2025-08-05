import redis

r = redis.Redis(decode_responses=True)

user_id = 'user:100'

# 해시 데이터 저장 (여러 필드를 한 번에 저장)
r.hset(user_id, mapping={
    'username': 'alice',
    'email': 'alice@example.com',
    'points': 150
})

# 특정 필드의 값 가져오기
username = r.hget(user_id, 'username')
print(f"사용자명: {username}")

# 해시의 모든 필드와 값 가져오기 (딕셔너리 형태로 반환)
user_info = r.hgetall(user_id)
print(f"사용자 정보: {user_info}")