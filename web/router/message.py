from fastapi import APIRouter, Depends, HTTPException
from web.dto.message import MessageFeedback, MessageFavorite
from common.constants.field.response import ResponseCode, OperationResponse
from web.fastapi_app import check_api_rate_limit

# 限流依赖提到路由级别，所有接口自动生效
router = APIRouter(dependencies=[Depends(check_api_rate_limit)])

# 模拟消息存储
messages = {
    "msg1": {"id": "msg1", "role": "user", "content": "Hello", "is_favorite": False, "feedback": 0},
    "msg2": {"id": "msg2", "role": "assistant", "content": "Hi there!", "is_favorite": False, "feedback": 0}
}

@router.post("/feedback", response_model=OperationResponse)
async def submit_feedback(feedback: MessageFeedback):
    """提交消息反馈"""
    message = messages.get(feedback.message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message["feedback"] = feedback.feedback

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data={"message": "Feedback submitted successfully"}
    )

@router.post("/favorite", response_model=OperationResponse)
async def toggle_favorite(favorite: MessageFavorite):
    """切换消息收藏状态"""
    message = messages.get(favorite.message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message["is_favorite"] = favorite.is_favorite

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data={"message": "Favorite status updated successfully"}
    )

@router.get("/favorites", response_model=OperationResponse)
async def get_favorite_messages():
    """获取收藏的消息"""
    favorite_messages = [msg for msg in messages.values() if msg.get("is_favorite", False)]

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data=favorite_messages
    )
