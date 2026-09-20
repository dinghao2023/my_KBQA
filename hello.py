import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 从 .env 文件读取 key，不会写死在代码里

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好，用一句话介绍一下你自己"}],
)

print(response.choices[0].message.content)