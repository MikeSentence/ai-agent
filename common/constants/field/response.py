# 响应相关常量

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class ResponseCode(Enum):
    """响应码枚举"""
    SUCCESS = (0, "成功")
    RATE_LIMIT_EXCEEDED = (429, "速率限制超出")
    SESSION_QUOTA_EXHAUSTED = (403, "会话额度耗尽")
    CONVERSATION_NOT_FOUND = (404, "会话不存在")
    INVALID_PARAMETER = (400, "参数无效")
    INTERNAL_ERROR = (500, "内部错误")
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class OperationResponse(BaseModel):
    """操作响应类"""
    code: int
    message: str
    data: Optional[Any] = None
