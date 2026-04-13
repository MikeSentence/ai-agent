from langchain_ollama import ChatOllama

_ollama_llm = ChatOllama(
    model="qwen3:8b",            # 需要 tool calling 支持，deepseek-r1 不支持
    base_url="http://localhost:11434",
    temperature=0.7,
    # num_predict=256,  # 限制生成长度
    # top_k=50,         # 采样参数
    # top_p=0.95,
)

def get_llm() -> ChatOllama:
    return _ollama_llm