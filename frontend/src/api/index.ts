import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ChatSession {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  session_id: string
  role: string
  content: string
  sources: string | null
  needs_clarification?: boolean
  created_at: string
}

export interface ChatResponse {
  session_id: string
  answer: string
  sources: string[]
  needs_clarification?: boolean
}

export interface SqlQuestion {
  id: string
  chapter: string
  title: string
  description: string
  difficulty: string
  hint: string | null
  reference_sql: string | null
  setup_sql: string | null
  tags: Record<string, string> | null
}

export interface SqlSubmitResult {
  id: string
  question_id: string
  user_sql: string
  is_correct: boolean
  score: number
  feedback: string | null
  execution_result: string | null
  created_at: string
  recommendations?: SqlPracticeRecommendation[]
}

export interface SqlPracticeRecommendation {
  type: 'knowledge' | 'practice'
  chapter?: string
  section?: string
  title: string
  reason: string
  node_id?: string | null
  question_id?: string
}

export interface KnowledgeNode {
  id: string
  parent_id: string | null
  chapter: string
  section: string
  title: string
  content: string | null
  sort_order: number
  children: KnowledgeNode[]
}

export const chatApi = {
  createSession: (title: string) => api.post<ChatSession>('/chat/sessions', { title }),
  listSessions: () => api.get<ChatSession[]>('/chat/sessions'),
  getMessages: (sessionId: string) => api.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`),
  deleteSession: (sessionId: string) => api.delete(`/chat/sessions/${sessionId}`),
  ask: (message: string, sessionId?: string) =>
    api.post<ChatResponse>('/chat/ask', { message, session_id: sessionId }),
  askStream: (message: string, sessionId?: string) =>
    fetch('/api/chat/ask/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
    }),
}

export const sqlApi = {
  listQuestions: (chapter?: string, difficulty?: string) =>
    api.get<SqlQuestion[]>('/sql-practice/questions', { params: { chapter, difficulty } }),
  getQuestion: (id: string) => api.get<SqlQuestion>(`/sql-practice/questions/${id}`),
  submit: (questionId: string, userSql: string) =>
    api.post<SqlSubmitResult>('/sql-practice/submit', { question_id: questionId, user_sql: userSql }),
  getSubmissions: (questionId: string) =>
    api.get<SqlSubmitResult[]>(`/sql-practice/submissions/${questionId}`),
  generate: (chapter: string, count: number = 5) =>
    api.post('/sql-practice/generate', null, { params: { chapter, count } }),
}

export const knowledgeApi = {
  getTree: () => api.get<{ nodes: KnowledgeNode[] }>('/knowledge-tree/tree'),
  search: (query: string, topK: number = 5) =>
    api.post('/knowledge-tree/search', { query, top_k: topK }),
  getChapters: () => api.get('/knowledge-tree/chapters'),
  getStats: () => api.get('/knowledge-tree/stats'),
}

export interface Recommendation {
  chapter: string
  section: string
  title: string
  reason: string
  node_id: string | null
}

export const recommendationApi = {
  getRecommendations: () => api.get<{ recommendations: Recommendation[] }>('/recommendations'),
}

export const adminApi = {
  ingest: (docxDir?: string) => api.post('/admin/ingest', null, { params: { docx_dir: docxDir } }),
  ingestStatus: () => api.get('/admin/ingest/status'),
  reset: () => api.post('/admin/reset'),
}

export default api