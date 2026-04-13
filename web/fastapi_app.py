from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from core import RedisClient, RateLimiter, SessionQuotaManager
from common.config.config import settings
from common.constants.field.response import ResponseCode


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时连接，关闭时断开"""
    # 启动：初始化连接，挂到 app.state
    app.state.redis_client = RedisClient(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
    )
    app.state.rate_limiter = RateLimiter(app.state.redis_client)
    app.state.session_quota_manager = SessionQuotaManager(app.state.redis_client)
    yield
    # 关闭：释放连接
    await app.state.redis_client.close()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 依赖注入：从 app.state 获取实例 ────────────────────────

def get_current_user_id(request: Request) -> str:
    return request.headers.get("X-User-ID", "anonymous")


def get_rate_limiter(request: Request) -> RateLimiter:
    return request.app.state.rate_limiter


def get_session_quota_manager(request: Request) -> SessionQuotaManager:
    return request.app.state.session_quota_manager


# ── 依赖注入：检查限流 / 额度 ─────────────────────────────

async def check_chat_rate_limit(
    user_id: str = Depends(get_current_user_id),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    if not await limiter.check_chat(user_id):
        raise HTTPException(
            status_code=ResponseCode.RATE_LIMIT_EXCEEDED.code,
            detail=ResponseCode.RATE_LIMIT_EXCEEDED.message
        )


async def check_api_rate_limit(
    user_id: str = Depends(get_current_user_id),
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    if not await limiter.check_api(user_id):
        raise HTTPException(
            status_code=ResponseCode.RATE_LIMIT_EXCEEDED.code,
            detail=ResponseCode.RATE_LIMIT_EXCEEDED.message
        )


# 导入路由
from web.router import chat, conversation, message

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["conversation"])
app.include_router(message.router, prefix="/api/message", tags=["message"])


# 根路径
@app.get("/")
async def read_root():
    return {"message": "AI Agent API is running"}


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
