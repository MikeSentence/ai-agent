# Redis相关常量

# 速率限制相关
RATE_LIMIT_CHAT_PREFIX = "rate_limit:chat:"
RATE_LIMIT_API_PREFIX = "rate_limit:api:"
RATE_LIMIT_CHAT_WINDOW = 3600  # 聊天接口限流窗口(秒)
RATE_LIMIT_CHAT_LIMIT = 100  # 聊天接口每窗口限制次数
RATE_LIMIT_API_WINDOW = 3600  # 普通接口限流窗口(秒)
RATE_LIMIT_API_LIMIT = 1000  # 普通接口每窗口限制次数

# 会话额度相关
SESSION_QUOTA_PREFIX = "session_quota:"
INITIAL_SESSION_QUOTA = 100  # 初始会话额度次数
