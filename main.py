import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

app = FastAPI()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

class Message(BaseModel):
    role: str
    content: str

@app.post("/chat")
async def chat(messages: list[Message]):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[m.model_dump() for m in messages],
    )
    return {"reply": response.choices[0].message.content}