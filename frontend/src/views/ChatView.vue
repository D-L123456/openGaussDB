<template>
  <div class="chat-view">
    <div class="chat-sidebar">
      <div class="chat-sidebar-header">
        <button class="btn btn-primary" @click="chatStore.createSession()">+ 新对话</button>
      </div>
      <div class="session-list">
        <div
          v-for="session in chatStore.sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: chatStore.currentSessionId === session.id }"
          @click="chatStore.selectSession(session.id)"
        >
          <span class="session-title">{{ session.title }}</span>
          <button class="session-delete" @click.stop="chatStore.deleteSession(session.id)">×</button>
        </div>
      </div>
    </div>
    <div class="chat-main">
      <div class="header">OpenGauss 知识问答</div>
      <div class="chat-body">
        <div class="chat-conversation">
          <div class="chat-messages" ref="messagesContainer">
            <div v-if="chatStore.messages.length === 0" class="empty-state">
              <div class="empty-icon">💬</div>
              <h3>向OpenGauss知识智能体提问</h3>
              <p>我可以回答关于openGauss数据库的安装、SQL、优化、迁移等问题</p>
              <div class="quick-questions">
                <button class="btn" @click="askQuick('如何在openEuler上安装openGauss？')">如何安装openGauss？</button>
                <button class="btn" @click="askQuick('openGauss中如何创建视图？')">如何创建视图？</button>
                <button class="btn" @click="askQuick('openGauss性能调优有哪些方法？')">性能调优方法</button>
                <button class="btn" @click="askQuick('如何从MySQL迁移到openGauss？')">MySQL迁移</button>
              </div>
            </div>
            <div
              v-for="msg in chatStore.messages"
              :key="msg.id"
              class="message"
              :class="msg.role"
            >
              <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
              <div class="message-body">
                <div v-if="msg.role === 'assistant'" class="assistant-message-wrapper" :class="{ 'is-clarification': msg.needs_clarification }">
                  <div v-if="msg.needs_clarification" class="clarification-badge">需要补充信息</div>
                  <div class="markdown-content" v-html="renderMarkdown(msg.content)"></div>
                </div>
                <div v-else class="message-text">{{ msg.content }}</div>
                <div v-if="msg.sources && msg.role === 'assistant' && !msg.needs_clarification" class="message-sources">
                  <span class="source-label">参考来源：</span>
                  <span v-for="(source, idx) in parseSources(msg.sources)" :key="idx" class="source-tag">{{ source }}</span>
                </div>
              </div>
            </div>
            <div v-if="chatStore.loading" class="message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-body">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <textarea
              v-model="inputText"
              @keydown.enter.exact="handleSend"
              placeholder="输入关于openGauss的问题..."
              rows="1"
            ></textarea>
            <button class="btn btn-primary" @click="handleSend" :disabled="chatStore.loading || !inputText.trim()">
              发送
            </button>
          </div>
        </div>
        <div v-if="recommendations.length > 0" class="rec-sidebar">
          <div class="rec-sidebar-header">
            <span>🎯 智能推荐</span>
            <button class="btn-toggle" @click="recCollapsed = !recCollapsed">{{ recCollapsed ? '◀' : '▶' }}</button>
          </div>
          <div v-if="!recCollapsed" class="rec-sidebar-body">
            <div
              v-for="(rec, idx) in recommendations"
              :key="idx"
              class="rec-card"
              @click="goToKnowledge(rec)"
            >
              <div class="rec-card-title">{{ rec.title }}</div>
              <div class="rec-card-chapter">{{ rec.chapter }}</div>
              <div class="rec-card-reason">{{ rec.reason }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { recommendationApi, type Recommendation } from '../api'
import { marked } from 'marked'

marked.setOptions({
  breaks: true,
  gfm: true,
})

const chatStore = useChatStore()
const router = useRouter()
const inputText = ref('')
const messagesContainer = ref<HTMLElement>()
const recommendations = ref<Recommendation[]>([])
const recCollapsed = ref(false)

onMounted(() => {
  chatStore.loadSessions().catch(console.error)
  loadRecommendations()
})

watch(() => chatStore.messages.length, async () => {
  await nextTick()
  scrollToBottom()
})

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function renderMarkdown(content: string): string {
  try {
    const result = marked.parse(content)
    if (typeof result === 'string') return result
    return content
  } catch {
    return content
  }
}

function parseSources(sources: string | null): string[] {
  if (!sources) return []
  try {
    return JSON.parse(sources)
  } catch {
    return []
  }
}

async function handleSend(e?: Event) {
  if (e instanceof KeyboardEvent && e.shiftKey) return
  e?.preventDefault()
  const text = inputText.value.trim()
  if (!text || chatStore.loading) return
  inputText.value = ''
  try {
    await chatStore.sendMessage(text)
  } catch (err) {
    console.error('发送失败:', err)
  }
  await nextTick()
  scrollToBottom()
}

async function askQuick(question: string) {
  inputText.value = ''
  try {
    await chatStore.sendMessage(question)
  } catch (err) {
    console.error('发送失败:', err)
  }
  await nextTick()
  scrollToBottom()
}

async function loadRecommendations() {
  try {
    const { data } = await recommendationApi.getRecommendations()
    recommendations.value = data.recommendations || []
  } catch {
    recommendations.value = []
  }
}

function goToKnowledge(rec: Recommendation) {
  router.push({ path: '/knowledge-tree', query: { nodeId: rec.node_id || undefined } })
}
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100%;
}

.chat-sidebar {
  width: 240px;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
}

.chat-sidebar-header {
  padding: 12px;
  border-bottom: 1px solid var(--border);
}

.chat-sidebar-header .btn {
  width: 100%;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.15s;
}

.session-item:hover {
  background: var(--bg);
}

.session-item.active {
  background: #eef4fd;
  color: var(--primary);
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-delete {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
  opacity: 0;
  transition: opacity 0.15s;
}

.session-item:hover .session-delete {
  opacity: 1;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  color: var(--text);
  margin-bottom: 8px;
}

.empty-state p {
  margin-bottom: 24px;
}

.rec-sidebar {
  width: 280px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.rec-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.btn-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 12px;
  padding: 2px 6px;
}

.rec-sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rec-card {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  border-left: 3px solid #f59e0b;
}

.rec-card:hover {
  border-color: var(--primary-light);
  background: #fafbfd;
}

.rec-card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 3px;
}

.rec-card-chapter {
  font-size: 11px;
  color: var(--primary);
  margin-bottom: 4px;
}

.rec-card-reason {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-body {
  max-width: 70%;
  min-width: 60px;
}

.message.user .message-body {
  text-align: right;
}

.message-text {
  background: #eef4fd;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  display: inline-block;
  text-align: left;
}

.message.assistant .markdown-content {
  font-size: 14px;
}

.assistant-message-wrapper {
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 14px 18px;
  border-radius: 12px;
}

.assistant-message-wrapper.is-clarification {
  background: #fffbeb;
  border-color: #fbbf24;
  border-left: 3px solid #f59e0b;
}

.clarification-badge {
  display: inline-block;
  background: #fef3c7;
  color: #92400e;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
}

.message-sources {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.source-label {
  margin-right: 4px;
}

.source-tag {
  display: inline-block;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  margin: 2px 4px 2px 0;
  font-size: 11px;
}


.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 14px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-secondary);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: var(--bg-card);
  border-top: 1px solid var(--border);
}

.chat-input textarea {
  flex: 1;
  resize: none;
  min-height: 40px;
  max-height: 120px;
  font-family: inherit;
}
</style>
