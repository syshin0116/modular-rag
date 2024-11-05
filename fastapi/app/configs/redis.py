import redis.asyncio as redis
from app.configs.settings import settings


class RedisClient:
    def __init__(self, url: str):
        self.url = url
        self.client = None

    async def connect(self):
        if self.client is None:
            self.client = redis.from_url(
                self.url, encoding="utf-8", decode_responses=True
            )
        return self.client

    async def disconnect(self):
        if self.client:
            await self.client.close()
            self.client = None


redis_client = RedisClient(url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")


async def get_redis():
    return await redis_client.connect()
