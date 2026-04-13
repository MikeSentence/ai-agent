from typing import Optional, List, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class MongoClient:
    """MongoDB 异步客户端封装（基于 motor）"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        db_name: str = "ai_agent",
        username: Optional[str] = None,
        password: Optional[str] = None,
        auth_source: str = "admin",
        max_pool_size: int = 10,
        min_pool_size: int = 2,
    ):
        connection_kwargs = {
            "host": host,
            "port": port,
            "maxPoolSize": max_pool_size,
            "minPoolSize": min_pool_size,
        }
        if username and password:
            connection_kwargs.update({
                "username": username,
                "password": password,
                "authSource": auth_source,
            })

        self._client: AsyncIOMotorClient = AsyncIOMotorClient(**connection_kwargs)
        self._db_name = db_name

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """获取默认数据库"""
        return self._client[self._db_name]

    def get_collection(self, name: str) -> AsyncIOMotorCollection:
        """获取集合"""
        return self.db[name]

    # ---------- 文档 CRUD ----------

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """插入单条文档，返回插入的 ID"""
        result = await self.get_collection(collection).insert_one(document)
        return str(result.inserted_id)

    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """插入多条文档，返回插入的 ID 列表"""
        result = await self.get_collection(collection).insert_many(documents)
        return [str(id_) for id_ in result.inserted_ids]

    async def find_one(self, collection: str, filter_: Dict[str, Any], projection: Optional[Dict] = None) -> Optional[Dict]:
        """查询单条文档"""
        return await self.get_collection(collection).find_one(filter_, projection)

    async def find_many(
        self,
        collection: str,
        filter_: Dict[str, Any],
        projection: Optional[Dict] = None,
        sort: Optional[List] = None,
        skip: int = 0,
        limit: int = 0,
    ) -> List[Dict]:
        """查询多条文档"""
        cursor = self.get_collection(collection).find(filter_, projection)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return await cursor.to_list(length=None)

    async def update_one(self, collection: str, filter_: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> int:
        """更新单条文档，返回匹配数"""
        result = await self.get_collection(collection).update_one(filter_, update, upsert=upsert)
        return result.matched_count

    async def update_many(self, collection: str, filter_: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> int:
        """更新多条文档，返回匹配数"""
        result = await self.get_collection(collection).update_many(filter_, update, upsert=upsert)
        return result.matched_count

    async def delete_one(self, collection: str, filter_: Dict[str, Any]) -> int:
        """删除单条文档，返回删除数"""
        result = await self.get_collection(collection).delete_one(filter_)
        return result.deleted_count

    async def delete_many(self, collection: str, filter_: Dict[str, Any]) -> int:
        """删除多条文档，返回删除数"""
        result = await self.get_collection(collection).delete_many(filter_)
        return result.deleted_count

    async def count_documents(self, collection: str, filter_: Dict[str, Any] = None) -> int:
        """统计文档数量"""
        return await self.get_collection(collection).count_documents(filter_ or {})

    # ---------- 索引管理 ----------

    async def create_index(self, collection: str, keys: List, unique: bool = False, name: Optional[str] = None) -> str:
        """创建索引"""
        return await self.get_collection(collection).create_index(keys, unique=unique, name=name)

    async def list_indexes(self, collection: str) -> List[Dict]:
        """列出集合索引"""
        return await self.get_collection(collection).list_indexes().to_list(length=None)

    # ---------- 生命周期 ----------

    async def ping(self) -> bool:
        """检查连接是否可用"""
        try:
            await self._client.admin.command("ping")
            return True
        except Exception:
            return False

    def close(self):
        """关闭连接"""
        self._client.close()
