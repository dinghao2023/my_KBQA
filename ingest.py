import os
import glob
import chromadb
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

ai = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)

def embed(texts):
    resp = ai.embeddings.create(model="BAAI/bge-m3", input=texts)
    return [d.embedding for d in resp.data]

# 1. 读取 docs 目录下所有文档
def load_documents():
    texts = []
    for path in glob.glob("docs/*.txt") + glob.glob("docs/*.md"):
        with open(path, encoding="utf-8") as f:
            texts.append((os.path.basename(path), f.read()))
    for path in glob.glob("docs/*.pdf"):
        reader = PdfReader(path)
        content = "\n".join(page.extract_text() or "" for page in reader.pages)
        texts.append((os.path.basename(path), content))
    return texts

# 2. 切分：每块约 500 字，相邻块重叠 50 字（防止把一句话拦腰截断）
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
)

chunks, metadatas = [], []
for name, content in load_documents():
    for piece in splitter.split_text(content):
        chunks.append(piece)
        metadatas.append({"source": name})

print(f"共切出 {len(chunks)} 个文本块")

# 3. 向量化并存入 Chroma（每批最多 16 条，避免一次请求太大）
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="knowledge")
collection.delete(collection.get()["ids"])  # 先清空，方便重复测试

BATCH = 16
for i in range(0, len(chunks), BATCH):
    batch = chunks[i:i+BATCH]
    collection.add(
        ids=[f"chunk_{j}" for j in range(i, i+len(batch))],
        documents=batch,
        embeddings=embed(batch),
        metadatas=metadatas[i:i+len(batch)],
    )

print("入库完成 ✅")