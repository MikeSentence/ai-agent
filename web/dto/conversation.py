from pydantic import BaseModel, Field
from typing import List


class ConversationCreate(BaseModel):
    name: str = Field(..., description="会话名称")


class ConversationUpdate(BaseModel):
    name: str = Field(..., description="新的会话名称")


class ConversationResponse(BaseModel):
    id: str = Field(..., description="会话ID")
    name: str = Field(..., description="会话名称")
    created_at: str = Field(..., description="创建时间")
    quota: int = Field(..., description="会话额度")


class ConversationList(BaseModel):
    conversations: List[ConversationResponse] = Field(..., description="会话列表")
