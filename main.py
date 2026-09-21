import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# 会话存储（内存版，重启服务就清空，P0 够用；后面会上数据库）
sessions: dict[str, list] = {}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    messages: list[Message]

class CreateSessionResponse(BaseModel):
    session_id: str

@app.post("/sessions", response_model=CreateSessionResponse)
def create_session():
    import uuid
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    return {"session_id": session_id}

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # 把这次新消息追加到历史记录里
    sessions[req.session_id].extend([m.model_dump() for m in req.messages])

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=sessions[req.session_id],
    )
    return {"reply": response.choices[0].message.content}