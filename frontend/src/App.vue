<script setup lang="ts">
import { ref } from 'vue'

const API_BASE = 'http://127.0.0.1:8000'

const file = ref<File | null>(null)
const question = ref('')
const answer = ref('')
const sources = ref<string[]>([])
const loading = ref(false)
const uploadMsg = ref('')

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  file.value = target.files?.[0] ?? null
}

const handleUpload = async () => {
  if (!file.value) return
  loading.value = true
  uploadMsg.value = ''
  try {
    const form = new FormData()
    form.append('file', file.value)
    const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: form })
    const data = await res.json()
    uploadMsg.value = `✅ ${data.filename} 已解析，生成 ${data.chunks} 个文本块`
  } catch {
    uploadMsg.value = '❌ 上传失败，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}

const handleAsk = async () => {
  if (!question.value.trim()) return
  loading.value = true
  answer.value = ''
  try {
    const res = await fetch(`${API_BASE}/ask?question=${encodeURIComponent(question.value)}`)
    const data = await res.json()
    answer.value = data.answer
    sources.value = data.sources || []
  } catch {
    answer.value = '请求失败，请确认后端服务已启动'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container">
    <h1>📚 My KBQA 知识库问答</h1>

    <section class="card">
      <h2>1. 上传文档（PDF）</h2>
      <input type="file" accept="application/pdf" @change="onFileChange" />
      <button :disabled="!file || loading" @click="handleUpload" style="margin-left: 12px">
        上传
      </button>
      <p v-if="uploadMsg" class="success">{{ uploadMsg }}</p>
    </section>

    <section class="card">
      <h2>2. 提问</h2>
      <div class="ask-row">
        <input
          v-model="question"
          placeholder="例如：讲一下 any 类型"
          @keyup.enter="handleAsk"
        />
        <button :disabled="loading" @click="handleAsk">发送</button>
      </div>
      <div v-if="answer" class="result">
        <p class="answer">{{ answer }}</p>
        <p v-if="sources.length" class="sources">📎 来源：{{ sources.join(', ') }}</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.container {
  max-width: 720px;
  margin: 40px auto;
  padding: 0 16px;
  font-family: system-ui, sans-serif;
}
h1 { font-size: 24px; }
.card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}
h2 { font-size: 16px; margin-top: 0; }
.ask-row { display: flex; gap: 8px; }
.ask-row input {
  flex: 1;
  padding: 8px 12px;
}
.success { margin-top: 8px; color: #059669; }
.result {
  margin-top: 16px;
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px;
}
.answer { white-space: pre-wrap; margin: 0; }
.sources { margin-top: 8px; color: #6b7280; font-size: 13px; }
</style>