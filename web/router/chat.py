from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from web.dto.chat import ChatRequest
from common.constants.field.response import ResponseCode
from web.fastapi_app import check_chat_rate_limit, get_session_quota_manager
from core.redis.limiter import SessionQuotaManager
import asyncio

# 限流依赖提到路由级别
router = APIRouter(dependencies=[Depends(check_chat_rate_limit)])

@router.post("/")
async def chat(
    request: ChatRequest,
    session_id: str,
    quota_mgr: SessionQuotaManager = Depends(get_session_quota_manager),
):
    """处理聊天请求（SSE协议）"""
    if not await quota_mgr.consume_quota(session_id):
        raise HTTPException(
            status_code=ResponseCode.SESSION_QUOTA_EXHAUSTED.code,
            detail=ResponseCode.SESSION_QUOTA_EXHAUSTED.message
        )

    async def generate_response():
        response_parts = ["Hello ", "this is ", "a streaming ", "response ", "from AI"]
        for part in response_parts:
            await asyncio.sleep(0.5)
            yield f"data: {part}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """获取聊天历史"""
    return {
        "session_id": session_id,
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }
