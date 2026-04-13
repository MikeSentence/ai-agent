# 应用配置

from pydantic_settings import BaseSettings
from typing import Optional, Any


class Settings(BaseSettings):
    """应用配置"""
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # MongoDB配置
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "ai_agent"
    mongo_username: Optional[str] = None
    mongo_password: Optional[str] = None
    mongo_auth_source: str = "admin"
    mongo_max_pool_size: int = 10
    mongo_min_pool_size: int = 2

    # Chroma配置
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "agent_memory"

    # 应用配置
    app_name: str = "AI Agent API"
    app_version: str = "0.1.0"
    app_description: str = "AI Agent Project API"

    # 服务器配置
    server_host: str = "0.0.0.0"
    server_port: int = 8080


    mem0_config: dict[str, Any] = {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "user_long_time_memory",  # 你希望使用的集合名称
                # "host": "localhost",  # 假设你的 Chroma 容器将端口映射到了宿主机
                # "port": 8000,  # Chroma 服务的默认端口
                "path": "./chromadb",         # 如果使用本地持久化，可以指定路径，与 host/port 二选一
            }
        },
        "llm": {
            "provider": "ollama",
            "config": {
                "model": "qwen3:8b",  # 与你的 Ollama 模型名称一致
                "ollama_base_url": "http://localhost:11434",
                "temperature": 0.1,
                "max_tokens": 2000,
            }
        },
        "embedder": {
            "provider": "ollama",
            "config": {
                "model": "qwen3-embedding:4b",  # 嵌入模型
                "ollama_base_url": "http://localhost:11434",
            }
        },
    }


# 创建配置实例
settings = Settings()
