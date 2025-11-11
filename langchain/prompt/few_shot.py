# ---------------------------------- 1. 静态 FewShot（固定示例，鲜花文案生成）----------------------------------
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
import os

# 1. 准备少样本示例（2个典型示例）
few_shot_examples = [
    {
        "flower": "玫瑰",
        "price": "50",
        "description": "50元红玫瑰象征热烈爱情，情人节告白首选～"
    },
    {
        "flower": "向日葵",
        "price": "45",
        "description": "45元向日葵传递阳光希望，送给朋友超暖心～"
    }
]

# 2. 定义示例模板（统一示例格式）
example_prompt = PromptTemplate(
    input_variables=["flower", "price", "description"],
    template="鲜花：{flower}（{price}元）\n文案：{description}\n"
)

# 3. 定义少样本提示模板
few_shot_prompt = FewShotPromptTemplate(
    examples=few_shot_examples,  # 静态示例列表
    example_prompt=example_prompt,  # 示例格式模板
    suffix="鲜花：{flower}（{price}元）\n文案：",  # 用户输入部分
    input_variables=["flower", "price"],  # 动态输入变量
    example_separator="\n---\n"  # 示例分隔符，提升可读性
)

# 4. 执行少样本生成
model = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="gpt-3.5-turbo"
)
chain = few_shot_prompt | model
result = chain.invoke({"flower": "勿忘我", "price": 32})
print("FewShot 文案：", result.content)
# 输出示例：32元勿忘我寓意永恒思念，送给长辈/朋友显心意～（模仿示例的“寓意+场景”逻辑）

# ---------------------------------- 2.动态 FewShot（语义相似性示例选择，更智能）----------------------------------
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os

# 1. 准备更多示例（4个）
all_examples = [
    {"flower": "玫瑰", "price": "50", "description": "50元红玫瑰象征热烈爱情，情人节告白首选～"},
    {"flower": "向日葵", "price": "45", "description": "45元向日葵传递阳光希望，送给朋友超暖心～"},
    {"flower": "康乃馨", "price": "20", "description": "20元康乃馨承载感恩，母亲节送给妈妈最贴心～"},
    {"flower": "百合", "price": "30", "description": "30元百合清雅圣洁，家居装饰/探望亲友皆可～"}
]

# 2. 动态示例选择器（根据输入语义选最相似的1个示例）
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=all_examples,
    embeddings=OpenAIEmbeddings(
        api_key=os.getenv("GPTSAPI_API_KEY"),
        base_url="https://api.gptsapi.net/v1"
    ),
    vectorstore_cls=Chroma,
    k=1  # 选1个最相似示例
)

# 3. 少样本提示模板（结合动态选择器）
few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,  # 复用上面的示例模板
    suffix="鲜花：{flower}（{price}元）\n文案：",
    input_variables=["flower", "price"]
)

# 4. 测试：输入“勿忘我”，动态选择最相似的“康乃馨”示例
chain = few_shot_prompt | model
result = chain.invoke({"flower": "勿忘我", "price": "32"})
print("动态 FewShot 文案：", result.content)
# 输出示例：32元勿忘我象征永恒思念，送给思念的人超显心意～（模仿“康乃馨+感恩”的“寓意+场景”逻辑）