import asyncio
from typing import List, Dict

from mem0 import Memory
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common.config.config import settings
from core.llm.ollama_client import get_llm
from common.utils.logger import Logger

logger = Logger(name="mem0")

# 初始化 LangChain 的 LLM 和 Mem0 的客户端
llm = get_llm()
mem0_client = Memory.from_config(settings.mem0_config)

# 定义 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="你是一个贴心的AI助手，能记住并利用过往对话信息，提供个性化回复。"),
    MessagesPlaceholder(variable_name="context"),
    HumanMessage(content="{input}")
])


async def retrieve_context(query: str, user_id: str) -> List[Dict]:
    """从 Mem0 检索与用户问题相关的记忆，并格式化为消息列表"""
    try:
        memories = await asyncio.to_thread(mem0_client.search, query, user_id=user_id)
        serialized_memories = " ".join([mem["memory"] for mem in memories.get('results', [])])
        if serialized_memories:
            return [{
                "role": "system",
                "content": f"以下是用户的相关记忆，请在回答时参考：{serialized_memories}"
            }]
    except Exception as e:
        logger.error("检索记忆失败: %s", e, exc_info=True)
    return [{"role": "user", "content": query}]


async def save_interaction(user_id: str, user_input: str, assistant_response: str):
    """将当前对话轮次保存到 Mem0 中"""
    try:
        messages = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": assistant_response}
        ]
        result = await asyncio.to_thread(mem0_client.add, messages, user_id=user_id)
        logger.debug("记忆保存成功: %d 条", len(result.get('results', [])))
    except Exception as e:
        logger.error("保存交互失败: %s", e, exc_info=True)


async def chat_turn(user_input: str, user_id: str) -> str:
    """处理单轮对话：检索记忆 -> 生成回复 -> 保存对话"""
    # 步骤1: 检索相关记忆
    context = await retrieve_context(user_input, user_id)

    # 步骤2: 调用 LangChain 异步生成回复
    chain = prompt | llm
    response = await chain.ainvoke({"context": context, "input": user_input})

    # 步骤3: 保存当前交互到 Mem0
    await save_interaction(user_id, user_input, response.content)

    return response.content
