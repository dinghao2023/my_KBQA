import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

ai = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)

def embed(texts):
    resp = ai.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [d.embedding for d in resp.data]

# 持久化客户端：数据存在本地 chroma_db 文件夹，重启不丢
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="knowledge")

docs = [
    "Python 是一种广泛用于后端和人工智能的编程语言。",
    "FastAPI 是一个高性能的 Python Web 框架，支持异步接口。",
    "React 是 Meta 开发的前端 UI 库，采用组件化开发。",
    "RAG 通过检索外部文档来增强大模型的回答，减少幻觉。",
]

# 写入（id 必须唯一；embeddings 直接用我们自己调 bge-m3 的结果）
# collection.add(
#     ids=[f"doc_{i}" for i in range(len(docs))],
#     documents=docs,
#     embeddings=embed(docs),
# )

# 检索
query = "怎么让大模型回答得更准确？"
result = collection.query(
    query_embeddings=embed([query]),
    n_results=2,  # 只取最相关的 2 条
)

print("问题：", query)
for doc, dist in zip(result["documents"][0], result["distances"][0]):
    print(f"距离 {dist:.4f}（越小越相似）  {doc}")