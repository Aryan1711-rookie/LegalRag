import os

from dotenv import load_dotenv
from redis import Redis

load_dotenv()

redis_client = Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)

def check_redis_connection() -> bool:
    try:
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection error: {e}")
        return False