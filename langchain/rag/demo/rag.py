import os

from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# --------------------------
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 推荐 gpt-3.5-turbo/gpt-4（支持工具调用）
    temperature=0.1,  # ReAct 需低温度，确保思考逻辑连贯
    timeout=30
)

# --------------------------
# 2. 文档加载与分割（核心：处理长文档）
# --------------------------
# 加载本地文档（示例：txt 文件，可替换为 PDFLoader/Docx2txtLoader 等）
loader = TextLoader("flower_knowledge.txt")  # 文档路径：存放鲜花知识（如养护、寓意等）
documents = loader.load()

# 文本分割：递归分割（按字符长度拆分，保留语义完整性）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # 每个片段 300 字符
    chunk_overlap=50,  # 片段重叠 50 字符（避免语义断裂）
    length_function=len  # 按字符数计算长度
)
split_docs = text_splitter.split_documents(documents)
print(f"📄 文档分割完成，共生成 {len(split_docs)} 个文本片段")

# --------------------------
# 3. 构建向量库（Chroma + 轻量嵌入模型）
# --------------------------
# 初始化嵌入模型（all-MiniLM-L6-v2：轻量、高效，适合本地运行）
embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 构建 Chroma 向量库（persist_directory 可选：持久化向量库，下次直接加载）
vector_db = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding,
    persist_directory="./chroma_flower_db"  # 向量库存储路径
)
# vector_db.persist()  # 持久化向量库（避免每次重新构建）

# --------------------------
# 4. 构建检索器（可选：添加上下文压缩，提升相关性）
# --------------------------
# 基础检索器：从向量库中检索 top3 相关片段
base_retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# 上下文压缩检索器（优化：用 LLM 过滤无关信息，提升检索质量）
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# --------------------------
# 5. 构建 RAG 链（最新版：create_retrieval_chain 简化配置）
# --------------------------
# 提示词模板（核心：告诉 LLM 基于检索到的上下文回答，避免幻觉）
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是鲜花知识专家，严格基于以下检索到的上下文信息回答用户问题：
    1. 只使用上下文提供的信息，不编造未提及的内容；
    2. 若上下文没有相关信息，直接回复“抱歉，没有找到相关鲜花知识”；
    3. 回答简洁明了，分点说明（如果需要）。
    上下文：{context}
    """),
    MessagesPlaceholder(variable_name="history", optional=True),  # 可选：支持对话历史
    ("human", "{input}")
])

# 构建「文档整合链」：将检索到的片段整合为上下文
combine_docs_chain = create_stuff_documents_chain(llm, prompt)

# 构建完整 RAG 链：检索 → 整合 → 生成
rag_chain = create_retrieval_chain(
    retriever=compression_retriever,  # 用压缩检索器（或 base_retriever）
    combine_docs_chain=combine_docs_chain
)

# --------------------------
# 6. 可选：添加对话历史（基于 RunnableWithMessageHistory）
# --------------------------
def get_session_history(session_id: str = "default") -> BaseChatMessageHistory:
    """多会话隔离存储（临时用字典，实际可替换为 Redis/MongoDB）"""
    if not hasattr(get_session_history, "session_store"):
        get_session_history.session_store = {}
    if session_id not in get_session_history.session_store:
        get_session_history.session_store[session_id] = InMemoryChatMessageHistory()
    return get_session_history.session_store[session_id]


# 绑定对话历史的 RAG 链（启用多轮对话需用此链）
rag_chain_with_history = RunnableWithMessageHistory(
    runnable=rag_chain,
    get_session_history=lambda :get_session_history(),
    input_messages_key="input",
    history_messages_key="history",
    session_id_key="session_id"
)

# --------------------------
# 7. 测试 RAG 链
# --------------------------
def test_rag():
    print("🚀 鲜花知识 RAG 助手（输入 'quit' 退出）")
    current_session_id = "user_001"  # 会话 ID（多用户时可动态分配）

    while True:
        user_input = input("\n你：")
        if user_input.lower() == "quit":
            print("👋 再见！")
            break

        # 执行 RAG 链（启用对话历史用 rag_chain_with_history）
        result = rag_chain_with_history.invoke(
            input={"input": user_input},
            config={"configurable": {"session_id": current_session_id}}
        )

        # 输出结果（result 包含 answer 和 context，可按需打印）
        print(f"助手：{result['answer']}")

        # 可选：打印检索到的相关上下文（调试用）
        # print("\n📌 检索到的相关信息：")
        # for i, doc in enumerate(result['context']['documents'], 1):
        #     print(f"{i}. {doc.page_content[:100]}...")


if __name__ == "__main__":
    test_rag()