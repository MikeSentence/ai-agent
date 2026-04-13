from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    id: Optional[str] = Field(None, description="消息ID")
    role: str = Field(..., description="角色(user, assistant)")
    content: str = Field(..., description="消息内容")
    created_at: Optional[str] = Field(None, description="创建时间")


class MessageFeedback(BaseModel):
    message_id: str = Field(..., description="消息ID")
    feedback: int = Field(..., ge=-1, le=1, description="反馈(-1: 负面, 0: 中性, 1: 正面)")


class MessageFavorite(BaseModel):
    message_id: str = Field(..., description="消息ID")
    is_favorite: bool = Field(..., description="是否收藏")
