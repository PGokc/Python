import os
from typing import List
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# -------------------------- 1. 依赖导入（确保已安装所有依赖）--------------------------
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader, Docx2txtLoader, \
    UnstructuredPDFLoader, UnstructuredFileLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


# -------------------------- 2. 全局配置（需手动修改的部分）--------------------------
class Config:
    # 知识库配置：文档存放目录（支持 PDF/TXT 文件）
    DOCS_DIR = "./docs"  # 请确保该文件夹存在，放入你的文档（如 PDF/TXT）
    # 向量数据库配置
    VECTOR_DB_DIR = "./chroma_rag_db"  # 向量数据持久化路径（自动创建）
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 轻量开源嵌入模型（无需 API Key）
    # 大模型配置
    OPENAI_API_KEY = os.getenv("GPTSAPI_API_KEY")  # 替换为你的 API Key（支持 gptsapi 兼容接口）
    OPENAI_BASE_URL = "https://api.gptsapi.net/v1"
    LLM_MODEL = "gpt-3.5-turbo"  # 可选：gpt-4、gpt-3.5-turbo-16k
    # RAG 流程配置
    CHUNK_SIZE = 500  # 文档分割片段长度（字）
    CHUNK_OVERLAP = 50  # 片段重叠长度（避免语义断裂）
    RETRIEVE_TOP_K = 3  # 检索时召回的相关片段数量（3-5 为宜）
    TEMPERATURE = 0.1  # 大模型温度（0.1-0.3 确保答案准确）


# 初始化配置实例
config = Config()


# -------------------------- 3. 工具函数：文档加载与处理--------------------------
def load_documents(docs_dir: str) -> List[Document]:
    """
    加载指定目录下的所有 PDF/TXT 文档
    :param docs_dir: 文档存放目录
    :return: 加载后的原始文档列表
    """
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"⚠️  文档目录 {docs_dir} 不存在，已自动创建，请放入 PDF/DOC/TXT 文档后重新运行")
        exit(1)

    # 定义加载器：支持 PDF 和 TXT 文件
    loaders = [
        DirectoryLoader(
            docs_dir,
            glob="*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
        ),
        DirectoryLoader(
            docs_dir,
            glob="*.docx",
            loader_cls=UnstructuredFileLoader,
            show_progress=True,
        ),
        DirectoryLoader(
            docs_dir,
            glob="*.txt",
            loader_cls=TextLoader,
            show_progress=True,
            loader_kwargs={"encoding": "utf-8"}
        ),
    ]

    # 加载所有文档
    documents = []
    for loader in loaders:
        try:
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"⚠️  加载 {loader.glob} 文档时出错：{str(e)}")

    if not documents:
        print(f"⚠️  未在 {docs_dir} 目录下找到 PDF/TXT 文档，请放入文档后重新运行")
        exit(1)

    print(f"✅ 成功加载 {len(documents)} 个文档")
    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    将长文档分割为短片段（适配模型上下文窗口）
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,  # 按字符数计算长度
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]  # 中文优先分割符
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ 文档分割完成，共得到 {len(chunks)} 个文本片段")
    return chunks


# -------------------------- 4. 初始化向量数据库与检索器--------------------------
def init_vector_db(chunks: List[Document]) -> Chroma:
    """
    初始化向量数据库，将文本片段向量化后存入
    """
    # 初始化嵌入模型（开源、轻量、无需 API Key）
    embedding = SentenceTransformerEmbeddings(model_name=config.EMBEDDING_MODEL)

    # 检查向量数据库是否已存在
    if os.path.exists(config.VECTOR_DB_DIR):
        # 加载已有数据库
        db = Chroma(
            persist_directory=config.VECTOR_DB_DIR,
            embedding_function=embedding
        )
        print(f"✅ 成功加载已存在的向量数据库（{config.VECTOR_DB_DIR}）")
    else:
        # 新建数据库并插入文本片段
        db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            persist_directory=config.VECTOR_DB_DIR
        )
        print(f"✅ 新建向量数据库完成，数据已保存至 {config.VECTOR_DB_DIR}")

    return db


def build_retriever(db: Chroma) -> RunnablePassthrough:
    """
    构建检索器（从向量数据库中召回相关片段）
    """
    retriever = db.as_retriever(
        search_kwargs={"k": config.RETRIEVE_TOP_K},
        search_type="similarity"  # 基础相似性检索（适合入门）
    )
    return retriever


# -------------------------- 5. 构建 RAG 流水线（检索+生成）--------------------------
def build_rag_chain(retriever: RunnablePassthrough) -> RunnablePassthrough:
    """
    构建完整 RAG 流水线：用户问题→检索相关文档→生成答案
    """
    # 初始化大模型
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        model=config.LLM_MODEL,
        temperature=config.TEMPERATURE,
        timeout=30
    )

    # 构建 Prompt（核心：引导模型基于检索文档生成答案）
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是一个基于参考文档的智能问答助手，严格遵循以下规则：
        1. 所有答案必须完全基于提供的参考文档片段，不添加任何外部知识；
        2. 若参考文档中没有与用户问题相关的信息，直接回复「未查询到相关信息」，禁止编造答案；
        3. 答案需简洁、有条理，优先使用分点形式呈现关键信息；
        4. 无需提及「根据参考文档」等表述，直接给出答案即可。
        """),
        ("user", "参考文档：\n{context}\n\n用户问题：{question}")
    ])

    # 构建流水线：检索→拼接上下文→Prompt→大模型→输出解析
    rag_chain = (
            {
                "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
                "question": RunnablePassthrough()  # 传递用户原始问题
            }
            | prompt
            | llm
            | StrOutputParser()  # 解析大模型输出为字符串
    )

    return rag_chain


# -------------------------- 6. 测试函数：交互式问答--------------------------
def interactive_qa(rag_chain: RunnablePassthrough):
    """
    交互式问答：持续接收用户问题，返回 RAG 生成的答案
    """
    print("\n" + "=" * 60)
    print("🎯 RAG 智能问答系统已启动（输入 '退出' 结束对话）")
    print("💡 提示：可询问文档中的相关问题（如产品功能、政策条款等）")
    print("=" * 60 + "\n")

    while True:
        user_input = input("用户：")
        if user_input.strip() in ["退出", "quit", "exit"]:
            print("助手：再见！有任何问题随时回来~")
            break
        if not user_input.strip():
            print("助手：请输入具体问题~")
            continue

        try:
            # 执行 RAG 流水线，生成答案
            answer = rag_chain.invoke(user_input)
            print(f"助手：{answer}\n")
        except Exception as e:
            print(f"⚠️  生成答案时出错：{str(e)}\n")


# -------------------------- 7. 主函数：串联全流程--------------------------
def main():
    try:
        # 步骤1：加载文档
        documents = load_documents(config.DOCS_DIR)

        # 步骤2：分割文档为短片段
        chunks = split_documents(documents)

        # 步骤3：初始化向量数据库
        db = init_vector_db(chunks)

        # 步骤4：构建检索器
        retriever = build_retriever(db)

        # 步骤5：构建 RAG 流水线
        rag_chain = build_rag_chain(retriever)

        # 步骤6：启动交互式问答
        interactive_qa(rag_chain)

    except Exception as e:
        print(f"❌ 系统运行出错：{str(e)}")


if __name__ == "__main__":
    main()