import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi, type ChatSession, type ChatMessage } from '../api'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  async function loadSessions() {
    try {
      const { data } = await chatApi.listSessions()
      sessions.value = data
    } catch (e) {
      console.error('加载会话失败:', e)
    }
  }

  async function createSession(title: string = '新对话') {
    const { data } = await chatApi.createSession(title)
    sessions.value.unshift(data)
    currentSessionId.value = data.id
    messages.value = []
    return data
  }

  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
    try {
      const { data } = await chatApi.getMessages(sessionId)
      messages.value = data
    } catch (e) {
      console.error('加载消息失败:', e)
      messages.value = []
    }
  }

  async function deleteSession(sessionId: string) {
    try {
      await chatApi.deleteSession(sessionId)
    } catch (e) {
      console.error('删除会话失败:', e)
    }
    sessions.value = sessions.value.filter(s => s.id !== sessionId)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = sessions.value.length > 0 ? sessions.value[0].id : null
      messages.value = []
    }
  }

  async function sendMessage(content: string) {
    let sessionId = currentSessionId.value

    if (!sessionId) {
      try {
        const session = await createSession(content.slice(0, 50))
        sessionId = session.id
        currentSessionId.value = session.id
      } catch (e) {
        console.error('创建会话失败:', e)
        messages.value.push({
          id: crypto.randomUUID(),
          session_id: '',
          role: 'assistant',
          content: '创建对话失败，请检查后端服务是否正常运行。',
          sources: null,
          created_at: new Date().toISOString(),
        })
        return
      }
    }

    messages.value.push({
      id: crypto.randomUUID(),
      session_id: sessionId,
      role: 'user',
      content,
      sources: null,
      created_at: new Date().toISOString(),
    })

    loading.value = true
    try {
      const { data } = await chatApi.ask(content, sessionId)
      messages.value.push({
        id: crypto.randomUUID(),
        session_id: data.session_id,
        role: 'assistant',
        content: data.answer,
        sources: JSON.stringify(data.sources),
        needs_clarification: data.needs_clarification || false,
        created_at: new Date().toISOString(),
      })
      if (data.session_id && data.session_id !== sessionId) {
        currentSessionId.value = data.session_id
      }
    } catch (e: any) {
      console.error('请求失败:', e)
      const errorMsg = e?.response?.data?.detail || e?.message || '请求失败，请稍后重试'
      messages.value.push({
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: 'assistant',
        content: `抱歉，请求失败：${errorMsg}`,
        sources: null,
        created_at: new Date().toISOString(),
      })
    } finally {
      loading.value = false
    }
  }

  return {
    sessions,
    currentSessionId,
    messages,
    loading,
    loadSessions,
    createSession,
    selectSession,
    deleteSession,
    sendMessage,
  }
})
