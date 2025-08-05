import redis

# Redis 연결
r = redis.Redis(decode_responses=True)

# 'name'이라는 키에 'Gemini'라는 값을 저장
r.set('name', 'Gemini')

# 'name' 키의 값을 가져와 출력
user_name = r.get('name')
print(f"이름: {user_name}")

# 존재하지 않는 키를 조회하면 None을 반환
non_existent = r.get('email')
print(f"존재하지 않는 키: {non_existent}")

# 키 만료 시간 설정 (10초 후에 자동으로 삭제)
r.set('session_id', 'xyz-123', ex=10)
print(f"세션 ID: {r.get('session_id')}")
# 10초 후에 다시 조회해보면 None이 출력됩니다.