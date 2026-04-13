import os
import time
from datetime import datetime, timedelta
from typing import Optional

from redis.commands.core import AsyncScript

from .client import RedisClient
from common.constants.field.redis import (
    RATE_LIMIT_CHAT_PREFIX, RATE_LIMIT_API_PREFIX,
    RATE_LIMIT_CHAT_WINDOW, RATE_LIMIT_CHAT_LIMIT,
    RATE_LIMIT_API_WINDOW, RATE_LIMIT_API_LIMIT,
    SESSION_QUOTA_PREFIX, INITIAL_SESSION_QUOTA,
)


def _load_lua(redis_client: RedisClient, filename: str) -> Optional[AsyncScript]:
    """从 resources/ 加载 Lua 脚本并注册到 Redis"""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return redis_client.client.register_script(f.read())


def _midnight_timestamp() -> int:
    """获取明天 0 点的 Unix 时间戳（秒）"""
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int(tomorrow.timestamp())


class RateLimiter:
    """速率限制器 — 基于 Lua 滑动窗口"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self._script = _load_lua(redis_client, "rate_limit.lua")

    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """检查是否允许请求

        Args:
            key: 完整的 Redis 键名（含前缀）
            limit: 窗口内允许的最大请求数
            window: 时间窗口（秒）
        """
        if self._script is None:
            raise RuntimeError("rate_limit.lua not found in resources/")
        now_ms = int(time.time() * 1000)
        result = await self._script(keys=[key], args=[str(limit), str(window), str(now_ms)])
        return bool(result)

    async def check_chat(self, user_id: str) -> bool:
        """检查聊天接口速率限制"""
        key = f"{RATE_LIMIT_CHAT_PREFIX}{user_id}"
        return await self.is_allowed(key, RATE_LIMIT_CHAT_LIMIT, RATE_LIMIT_CHAT_WINDOW)

    async def check_api(self, user_id: str) -> bool:
        """检查普通接口速率限制"""
        key = f"{RATE_LIMIT_API_PREFIX}{user_id}"
        return await self.is_allowed(key, RATE_LIMIT_API_LIMIT, RATE_LIMIT_API_WINDOW)


class SessionQuotaManager:
    """会话额度管理器 — Lua 脚本内自动初始化，过期到当晚 0 点"""

    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self._script = _load_lua(redis_client, "session_quota.lua")

    async def _execute(self, session_id: str, operation: str, amount: int = 0) -> int:
        if self._script is None:
            raise RuntimeError("session_quota.lua not found in resources/")
        key = f"{SESSION_QUOTA_PREFIX}{session_id}"
        midnight = _midnight_timestamp()
        return await self._script(
            keys=[key],
            args=[operation, str(amount), str(INITIAL_SESSION_QUOTA), str(midnight)],
        )

    async def get_quota(self, session_id: str) -> int:
        """获取会话额度（key 不存在时自动初始化）"""
        return await self._execute(session_id, "get")

    async def update_quota(self, session_id: str, amount: int) -> int:
        """增减会话额度（key 不存在时自动初始化）"""
        return await self._execute(session_id, "update", amount)

    async def consume_quota(self, session_id: str, amount: int = 1) -> bool:
        """消耗会话额度（key 不存在时自动初始化）"""
        result = await self._execute(session_id, "consume", amount)
        return bool(result)
