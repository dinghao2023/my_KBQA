import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)

def embed(texts):
    resp = client.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [d.embedding for d in resp.data]

# 4 段"知识库"
docs = [
    "Python 是一种广泛用于后端和人工智能的编程语言。",
    "FastAPI 是一个高性能的 Python Web 框架，支持异步接口。",
    "React 是 Meta 开发的前端 UI 库，采用组件化开发。",
    "RAG 通过检索外部文档来增强大模型的回答，减少幻觉。",
]

doc_vecs = np.array(embed(docs))

query = "怎么让大模型回答得更准确？"
q_vec = np.array(embed([query]))[0]

# 余弦相似度：值越大越相关
sims = doc_vecs @ q_vec / (np.linalg.norm(doc_vecs, axis=1) * np.linalg.norm(q_vec))

print("问题：", query)
for i in np.argsort(-sims):
    print(f"{sims[i]:.4f}  {docs[i]}")