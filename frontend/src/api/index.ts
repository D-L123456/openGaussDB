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

export interface LearningEvent {
  id: string
  event_type: string
  level: number | null
  part: number | null
  detail: Record<string, any> | null
  duration_seconds: number | null
  created_at: string
}

export interface UserProfile {
  user_id: string
  ability_scores: Record<string, any>
  weak_points: Record<string, any> | null
  error_patterns: Record<string, any> | null
  learning_style: string
  total_learning_time: number
  streak_days: number
  last_active_at: string | null
  challenge_progress: Record<string, any> | null
  badges: Record<string, any> | null
}

export interface LearningRecommendation {
  id: string
  rec_type: string
  title: string
  description: string
  priority: number
  action_type: string | null
  action_target: string | null
  is_read: boolean
  created_at: string
}

export interface ErrorPattern {
  id: string
  category: string
  description: string
  occurrence_count: number
  ability_dim: string | null
  last_seen_at: string
}

export interface AbilitySnapshot {
  id: string
  ability_scores: Record<string, any>
  trigger_event: string
  created_at: string
}

export interface LearningDashboard {
  profile: UserProfile
  recent_recommendations: LearningRecommendation[]
  top_error_patterns: ErrorPattern[]
  ability_history: AbilitySnapshot[]
  timeline: Record<string, any>[]
}

export const learningApi = {
  recordEvent: (data: { event_type: string; level?: number; part?: number; detail?: Record<string, any>; duration_seconds?: number }) =>
    api.post<LearningEvent>('/learning/events', data),
  getEvents: (eventType?: string, limit?: number) =>
    api.get<LearningEvent[]>('/learning/events', { params: { event_type: eventType, limit } }),
  getProfile: () => api.get<UserProfile>('/learning/profile'),
  getRecommendations: (refresh?: boolean) =>
    api.get<LearningRecommendation[]>('/learning/recommendations', { params: { refresh } }),
  markRecommendationRead: (recId: string) =>
    api.put(`/learning/recommendations/${recId}/read`),
  dismissRecommendation: (recId: string) =>
    api.put(`/learning/recommendations/${recId}/dismiss`),
  getErrorPatterns: () => api.get<ErrorPattern[]>('/learning/error-patterns'),
  getAbilityHistory: (limit?: number) =>
    api.get<AbilitySnapshot[]>('/learning/ability-history', { params: { limit } }),
  getTimeline: (days?: number) =>
    api.get('/learning/timeline', { params: { days } }),
  getDashboard: () => api.get<LearningDashboard>('/learning/dashboard'),
  markKnowledgeRead: (nodeId: string) => api.post(`/learning/knowledge-read/${nodeId}`),
  getKnowledgeRead: () => api.get<{ read_node_ids: string[]; node_titles: Record<string, string> }>('/learning/knowledge-read'),
}

export const adminApi = {
  ingest: (docxDir?: string) => api.post('/admin/ingest', null, { params: { docx_dir: docxDir } }),
  ingestStatus: () => api.get('/admin/ingest/status'),
  reset: () => api.post('/admin/reset'),
}

export default api