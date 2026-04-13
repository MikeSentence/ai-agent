"""RAG 工具模块：将向量检索封装为 LangGraph Tool，集成到 Supervisor 工作流中"""

from langchain_core.tools import tool
from core.vector_store import ChromaStore
from common.config.config import settings

# 全局 ChromaStore 实例（懒加载）
_chroma_store: ChromaStore | None = None


def _get_chroma_store() -> ChromaStore:
    """获取 ChromaStore 单例"""
    global _chroma_store
    if _chroma_store is None:
        _chroma_store = ChromaStore(
            collection_name=settings.chroma_collection_name,
            persist_dir=settings.chroma_persist_dir,
        )
    return _chroma_store


@tool
async def rag_search(query: str, k: int = 4) -> str:
    """在知识库中检索与问题相关的文档片段。

    当需要查找事实性知识、文档内容或历史信息时使用此工具。
    返回最相关的文档片段，供后续回答参考。

    Args:
        query: 检索查询文本，通常是用户的问题或关键词。
        k: 返回的结果数量，默认 4。
    """
    store = _get_chroma_store()
    results = await store.similarity_search(query, k=k)

    if not results:
        return "未在知识库中找到相关内容。"

    # 格式化检索结果
    formatted = []
    for i, doc in enumerate(results, 1):
        score = f" (相关度: {doc['score']:.4f})" if doc.get("score") is not None else ""
        formatted.append(f"[{i}]{score} {doc['text']}")

    return "\n".join(formatted)


@tool
async def rag_add_documents(documents: list[str], metadatas: list[dict] | None = None) -> str:
    """向知识库中添加文档，供后续检索使用。

    Args:
        documents: 要添加的文档文本列表。
        metadatas: 可选的元数据列表，每条文档对应一个字典。
    """
    store = _get_chroma_store()
    await store.add_documents(docs=documents, metadatas=metadatas)
    return f"成功添加 {len(documents)} 条文档到知识库。"


# 导出所有工具，方便在 Supervisor 中注册
rag_tools = [rag_search, rag_add_documents]
