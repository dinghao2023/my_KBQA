import os
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Embedding 用硅基流动，对话用 DeepSeek
embed_client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)
chat_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="knowledge")

def ask(question):
    # 1. 把问题向量化，捞出最相关的 3 块
    q_emb = embed_client.embeddings.create(
        model="BAAI/bge-m3", input=[question]
    ).data[0].embedding

    result = collection.query(query_embeddings=[q_emb], n_results=3)
    contexts = result["documents"][0]
    sources = [m["source"] for m in result["metadatas"][0]]

    # 2. 把检索到的内容拼进 prompt（这是 RAG 的灵魂：先给资料，再让它答）
    context_text = "\n\n---\n\n".join(contexts)
    prompt = f"""请严格根据下面提供的参考资料回答用户问题。
如果资料中没有相关内容，就直接说"根据现有资料无法回答"，不要自己编造。
回答简洁准确，并在结尾标注信息来源。

参考资料：
{context_text}

用户问题：{question}"""

    # 3. 调 DeepSeek 生成
    response = chat_client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content, sources

# 交互式问答：输入问题回车，输入 q 退出
if __name__ == "__main__":
    while True:
        q = input("\n请提问（输入 q 退出）：").strip()
        if q.lower() == "q":
            break
        if not q:
            continue
        answer, sources = ask(q)
        print("\n🤖", answer)
        print("📎 来源：", ", ".join(sorted(set(sources))))