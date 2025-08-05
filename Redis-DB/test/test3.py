import redis

r = redis.Redis(decode_responses=True)

log_key = 'system_logs'

# 리스트에 로그 추가 (왼쪽부터 추가됨)
r.lpush(log_key, 'INFO: User logged in')
r.lpush(log_key, 'WARNING: Disk space low')
r.lpush(log_key, 'ERROR: Connection failed')

# 리스트의 모든 항목 조회 (0부터 -1까지)
logs = r.lrange(log_key, 0, -1)
print(f"전체 로그: {logs}")

# 리스트에서 데이터 꺼내기 (가장 나중에 들어간 ERROR 로그부터 나옴)
latest_log = r.lpop(log_key)
print(f"처리한 로그: {latest_log}")

# 데이터 꺼낸 후 리스트 상태 확인
remaining_logs = r.lrange(log_key, 0, -1)
print(f"남은 로그: {remaining_logs}")