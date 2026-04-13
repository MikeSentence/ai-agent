from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="聊天消息内容")
    model: str = Field(default="gpt-3.5-turbo", description="使用的模型")


class ChatResponse(BaseModel):
    message: str = Field(..., description="聊天响应内容")
    session_id: str = Field(..., description="会话ID")
    model: str = Field(..., description="使用的模型")
