from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VectorStore(ABC):
    """统一的向量数据库接口"""

    @abstractmethod
    async def add_documents(self, docs: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        """添加文档（自动向量化）"""
        pass

    @abstractmethod
    async def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """相似度检索，返回 [{'id':..., 'text':..., 'metadata':..., 'score':...}]"""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]):
        """删除指定 ID 的文档"""
        pass

    @abstractmethod
    async def clear(self):
        """清空所有数据"""
        pass
