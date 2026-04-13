import asyncio
from typing import Optional, List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions

from core.vector_store.base import VectorStore


class ChromaStore(VectorStore):
    """ChromaDB 向量存储实现

    注意：ChromaDB 本身无异步 API，内部操作通过 asyncio.to_thread 转为异步调用，
    避免阻塞事件循环。
    """

    def __init__(self, collection_name: str = "agent_memory", persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn
        )

    async def add_documents(self, docs: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        if ids is None:
            ids = [f"id_{i}" for i in range(len(docs))]
        await asyncio.to_thread(
            self.collection.add,
            documents=docs,
            metadatas=metadatas or [{}] * len(docs),
            ids=ids,
        )

    async def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        results = await asyncio.to_thread(
            self.collection.query,
            query_texts=[query],
            n_results=k,
        )
        out = []
        for i in range(len(results['ids'][0])):
            out.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': results['distances'][0][i] if 'distances' in results else None
            })
        return out

    async def delete(self, ids: List[str]):
        await asyncio.to_thread(self.collection.delete, ids=ids)

    async def clear(self):
        await asyncio.to_thread(self.client.delete_collection, self.collection.name)
        self.collection = await asyncio.to_thread(
            self.client.create_collection,
            name=self.collection.name,
            embedding_function=self.embed_fn,
        )
