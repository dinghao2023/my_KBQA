# My KBQA · 知识库智能问答

基于 RAG 的个人知识库问答系统：上传 PDF 文档，即可用自然语言提问，
AI 严格依据文档内容回答，并标注来源；文档中没有的内容会明确拒绝，不编造。

## 技术架构
- **后端**：Python + FastAPI + Uvicorn
- **RAG 链路**：PDF 解析（pypdf）→ 文本切分（LangChain Recursive Splitter）
  → Embedding（bge-m3）→ 向量数据库（Chroma）→ 语义检索 → Prompt 增强 → 生成
- **模型**：DeepSeek（对话生成）、bge-m3 via 硅基流动（向量化）
- **前端**：Vue 3 + TypeScript + Vite

## 核心流程
1. `/upload`：上传 PDF → 解析 → 切分为 500 字小块（50 字重叠）→ 向量化存入 Chroma
2. `/ask`：问题向量化 → 检索 Top3 相关块 → 拼入 Prompt → DeepSeek 基于资料生成回答

## 本地运行
\`\`\`bash
# 后端
pip install -r requirements.txt
uvicorn app:app --reload

# 前端
cd frontend && npm install && npm run dev
\`\`\`
需要在根目录创建 .env：
DEEPSEEK_API_KEY=xxx
SILICONFLOW_API_KEY=xxx

## Docker 部署
\`\`\`bash
docker build -t my-kbqa .
docker run -p 8000:8000 --env-file .env my-kbqa
\`\`\`