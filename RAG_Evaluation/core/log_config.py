import logging
import json
from cache_redis import get_cache, set_cache  # 이미 쓰고 있는 유틸

# Redis에 session_log로 append하는 Handler
class RedisSessionHandler(logging.Handler):
    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id
        self.formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        )

    def emit(self, record):
        try:
            log_entry = self.format(record)  # logging 포맷터 적용
            session_data = get_cache(self.session_id)
            if session_data is None:
                session_data = {"session_log": []}
            else:
                session_data = json.loads(session_data)

            session_data.setdefault("session_log", []).append(log_entry)
            set_cache(self.session_id, session_data)
        except Exception as e:
            print(f"Redis logging failed: {e}")
