from typing import Optional, Dict

import redis.asyncio as aioredis


class RedisClient:
    """Redis 异步客户端封装 — 只提供纯粹的 Redis 操作"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        self.client = aioredis.Redis(
            host=host, port=port, db=db, password=password, decode_responses=True
        )

    # ---------- 基础操作 ----------

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        if expire:
            return await self.client.setex(key, expire, value)
        return await self.client.set(key, value)

    async def delete(self, key: str) -> int:
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def incr(self, key: str) -> int:
        return await self.client.incr(key)

    async def decr(self, key: str) -> int:
        return await self.client.decr(key)

    # ---------- Hash 操作 ----------

    async def hget(self, key: str, field: str) -> Optional[str]:
        return await self.client.hget(key, field)

    async def hset(self, key: str, field: str, value: str) -> int:
        return await self.client.hset(key, field, value)

    async def hgetall(self, key: str) -> Dict[str, str]:
        return await self.client.hgetall(key)

    async def hdel(self, key: str, *fields: str) -> int:
        return await self.client.hdel(key, *fields)

    # ---------- List 操作 ----------

    async def lpush(self, key: str, *values: str) -> int:
        return await self.client.lpush(key, *values)

    async def rpush(self, key: str, *values: str) -> int:
        return await self.client.rpush(key, *values)

    async def lrange(self, key: str, start: int, end: int) -> list:
        return await self.client.lrange(key, start, end)

    # ---------- Set 操作 ----------

    async def sadd(self, key: str, *members: str) -> int:
        return await self.client.sadd(key, *members)

    async def smembers(self, key: str) -> set:
        return await self.client.smembers(key)

    async def srem(self, key: str, *members: str) -> int:
        return await self.client.srem(key, *members)

    # ---------- 生命周期 ----------

    async def ping(self) -> bool:
        """检查连接是否可用"""
        return await self.client.ping()

    async def close(self):
        """关闭连接"""
        await self.client.aclose()
