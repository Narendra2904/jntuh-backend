import os
import redis
import json

# 🔥 Read Redis URL from environment (local or cloud)
REDIS_URL = os.getenv("REDIS_URL")

try:
    if REDIS_URL:
        redis_client = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1
        )
    else:
        # Local fallback (only for local dev)
        redis_client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=1
        )

    redis_client.ping()
    REDIS_AVAILABLE = True

except Exception:
    redis_client = None
    REDIS_AVAILABLE = False


CACHE_TTL = 60 * 60 * 12  # 12 hours


def get_cache(key):
    if not REDIS_AVAILABLE:
        return None
    try:
        data = redis_client.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


def set_cache(key, value):
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.set(key, json.dumps(value))
    except Exception:
        pass
