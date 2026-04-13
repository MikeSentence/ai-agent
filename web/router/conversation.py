from fastapi import APIRouter, Depends, HTTPException
from web.dto.conversation import ConversationCreate, ConversationResponse, ConversationList, ConversationUpdate
from common.constants.field.redis import INITIAL_SESSION_QUOTA
from common.constants.field.response import ResponseCode, OperationResponse
from web.fastapi_app import check_api_rate_limit, get_session_quota_manager
from core.redis.limiter import SessionQuotaManager
import uuid

# 限流依赖提到路由级别
router = APIRouter(dependencies=[Depends(check_api_rate_limit)])

# 模拟会话存储
conversations = {}

@router.post("/", response_model=OperationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    quota_mgr: SessionQuotaManager = Depends(get_session_quota_manager),
):
    """创建新会话"""
    session_id = str(uuid.uuid4())

    # 初始化会话额度
    await quota_mgr.update_quota(session_id, INITIAL_SESSION_QUOTA)

    conversations[session_id] = {
        "id": session_id,
        "name": conversation.name,
        "created_at": "2024-01-01T00:00:00Z",
        "quota": INITIAL_SESSION_QUOTA
    }

    response_data = ConversationResponse(
        id=session_id,
        name=conversation.name,
        created_at="2024-01-01T00:00:00Z",
        quota=INITIAL_SESSION_QUOTA
    )

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data=response_data
    )

@router.get("/", response_model=OperationResponse)
async def get_conversations():
    """获取会话列表"""
    conversation_list = [
        ConversationResponse(**conv) for conv in conversations.values()
    ]

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data=ConversationList(conversations=conversation_list)
    )

@router.get("/{session_id}", response_model=OperationResponse)
async def get_conversation(
    session_id: str,
    quota_mgr: SessionQuotaManager = Depends(get_session_quota_manager),
):
    """获取会话详情"""
    conversation = conversations.get(session_id)
    if not conversation:
        raise HTTPException(
            status_code=ResponseCode.CONVERSATION_NOT_FOUND.code,
            detail=ResponseCode.CONVERSATION_NOT_FOUND.message
        )

    conversation["quota"] = await quota_mgr.get_quota(session_id)

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data=ConversationResponse(**conversation)
    )

@router.put("/{session_id}", response_model=OperationResponse)
async def update_conversation(
    session_id: str,
    conversation_update: ConversationUpdate,
):
    """修改会话"""
    conversation = conversations.get(session_id)
    if not conversation:
        raise HTTPException(
            status_code=ResponseCode.CONVERSATION_NOT_FOUND.code,
            detail=ResponseCode.CONVERSATION_NOT_FOUND.message
        )

    conversation["name"] = conversation_update.name

    return OperationResponse(
        code=ResponseCode.SUCCESS.code,
        message=ResponseCode.SUCCESS.message,
        data=ConversationResponse(**conversation)
    )

@router.delete("/{session_id}", response_model=OperationResponse)
async def delete_conversation(session_id: str):
    """删除会话"""
    if session_id in conversations:
        del conversations[session_id]
        return OperationResponse(
            code=ResponseCode.SUCCESS.code,
            message=ResponseCode.SUCCESS.message,
            data={"message": "Conversation deleted"}
        )
    else:
        raise HTTPException(
            status_code=ResponseCode.CONVERSATION_NOT_FOUND.code,
            detail=ResponseCode.CONVERSATION_NOT_FOUND.message
        )
