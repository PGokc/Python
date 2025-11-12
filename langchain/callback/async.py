import os
import asyncio
import aiofiles
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import AsyncCallbackHandler
from typing import Dict, Any, Optional

# -------------------------- 1. 自定义异步回调处理器（核心）--------------------------
class AsyncFileWriteCallback(AsyncCallbackHandler):
    """异步回调处理器：将 LLM 输出异步写入文件，不阻塞主流程"""
    def __init__(self, file_path: str = "llm_output.txt", encoding: str = "utf-8"):
        self.file_path = file_path  # 输出文件路径
        self.encoding = encoding    # 文件编码
        self.file: Optional[aiofiles.AsyncFile] = None  # 异步文件对象（延迟初始化）

    # 异步初始化文件（避免重复打开）
    async def _init_file(self):
        if self.file is None:
            # mode="a"：追加模式（避免覆盖历史内容）；newline=""：保持换行一致
            self.file = await aiofiles.open(self.file_path, mode="a", encoding=self.encoding)

    # 【流式场景】LLM 生成新 Token 时触发（逐字写入文件）
    async def on_llm_new_token_async(self, token: str, **kwargs) -> None:
        await self._init_file()  # 懒加载文件对象
        await self.file.write(token)  # 异步写入 Token（非阻塞）
        await self.file.flush()  # 可选：立即刷新缓冲区（确保实时写入）

    # 【非流式场景】LLM 调用结束时触发（一次性写入完整输出）
    async def on_llm_end_async(self, response: Any, **kwargs) -> None:
        await self._init_file()
        # 非流式响应：response 是 AIMessage 对象，content 为完整内容
        full_content = response.content + "\n\n"  # 换行分隔不同请求
        await self.file.write(full_content)
        await self.file.flush()

    # 【通用】LLM 调用出错时触发（关闭文件+记录错误）
    async def on_llm_error_async(self, error: Exception, **kwargs) -> None:
        print(f"❌ LLM 调用出错：{str(error)}")
        if self.file is not None:
            await self.file.write(f"\n[错误] {str(error)}\n\n")
            await self.file.close()
            self.file = None

    # 【通用】所有事件结束后关闭文件（避免资源泄露）
    async def close(self):
        if self.file is not None:
            await self.file.close()
            self.file = None

# -------------------------- 2. 基础配置（LLM + Prompt）--------------------------
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 GPTSAPI_API_KEY")

# 初始化异步 LLM（支持 async invoke/astream）
llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://api.gptsapi.net/v1",
    model="gpt-3.5-turbo",
    temperature=0.7,
    streaming=False,  # 默认为非流式；流式场景需设为 True
    callbacks=[AsyncFileWriteCallback(file_path="llm_async_output.txt")]  # 注册异步回调
)

# 定义 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是专业的技术助手，回答简洁明了。"),
    ("human", "{input}")
])

# 组装异步 Runnable 链（Prompt + LLM）
async_chain = prompt | llm

# -------------------------- 3. 测试场景（非流式 + 流式）--------------------------
async def test_non_streaming():
    """测试非流式异步调用：LLM 生成完整响应后，回调一次性写入文件"""
    print("=== 测试非流式异步写入 ===")
    result = await async_chain.ainvoke({"input": "用 3 句话介绍异步回调的优势"})
    print(f"非流式响应：{result.content}")
    # 关闭文件（确保内容写入）
    await async_chain.callbacks[0].close()

async def test_streaming():
    """测试流式异步调用：LLM 逐字生成响应，回调逐字写入文件"""
    print("\n=== 测试流式异步写入 ===")
    # 临时修改 LLM 为流式模式（不影响全局配置）
    streaming_llm = llm.copy(update={"streaming": True})
    streaming_chain = prompt | streaming_llm

    print("流式响应（实时打印+异步写入文件）：", end="", flush=True)
    # 异步流式调用：迭代生成器获取 Token
    async for chunk in streaming_chain.astream({"input": "用 3 句话介绍 LangChain 异步生态"}):
        print(chunk.content, end="", flush=True)  # 实时打印到控制台
    print()  # 换行
    # 关闭文件
    await streaming_chain.callbacks[0].close()

# -------------------------- 4. 运行测试（主函数）--------------------------
if __name__ == "__main__":
    # 执行异步测试（非流式 + 流式）
    asyncio.run(test_non_streaming())
    asyncio.run(test_streaming())

    # 验证结果
    print("\n✅ 测试完成！请查看文件：llm_async_output.txt")