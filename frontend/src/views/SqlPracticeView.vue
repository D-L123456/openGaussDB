<template>
  <div class="sql-practice-view">
    <div class="header">SQL 练习与判题</div>
    <div class="content-area">
      <div class="sql-layout">
        <div class="question-panel">
          <div class="card">
            <div class="filter-bar">
              <select v-model="filterChapter" @change="loadQuestions">
                <option value="">全部章节</option>
                <option value="第1章">第1章 使用数据库</option>
                <option value="第2章">第2章 数据优化和封装</option>
                <option value="第3章">第3章 数据库设计</option>
                <option value="第4章">第4章 数据库开发</option>
                <option value="第5章">第5章 数据库迁移</option>
                <option value="第6章">第6章 性能调优</option>
                <option value="第7章">第7章 高级特性</option>
              </select>
              <select v-model="filterDifficulty" @change="loadQuestions">
                <option value="">全部难度</option>
                <option value="easy">简单</option>
                <option value="medium">中等</option>
                <option value="hard">困难</option>
              </select>
            </div>
            <div class="question-list">
              <div
                v-for="q in questions"
                :key="q.id"
                class="question-item"
                :class="{ active: selectedQuestion?.id === q.id }"
                @click="selectQuestion(q)"
              >
                <div class="question-title">{{ q.title }}</div>
                <div class="question-meta">
                  <span class="chapter-tag">{{ q.chapter }}</span>
                  <span class="difficulty-tag" :class="q.difficulty">{{ difficultyLabel(q.difficulty) }}</span>
                </div>
              </div>
              <div v-if="questions.length === 0" class="empty-hint">
                暂无题目，请先通过管理接口导入或生成题目
              </div>
            </div>
          </div>
        </div>
        <div class="editor-panel">
          <div v-if="selectedQuestion" class="card">
            <h3 class="question-detail-title">{{ selectedQuestion.title }}</h3>
            <div class="question-description">{{ selectedQuestion.description }}</div>
            <div v-if="selectedQuestion.hint" class="question-hint">
              <strong>提示：</strong>{{ selectedQuestion.hint }}
            </div>
            <div class="sql-editor">
              <div class="editor-header">
                <span>SQL 编辑器</span>
                <div class="editor-actions">
                  <button class="btn" @click="formatSql">格式化</button>
                  <button class="btn" @click="clearEditor">清空</button>
                </div>
              </div>
              <textarea
                v-model="userSql"
                class="sql-textarea"
                placeholder="在此编写openGauss兼容的SQL语句..."
                spellcheck="false"
              ></textarea>
            </div>
            <div class="submit-bar">
              <button class="btn btn-primary" @click="submitAnswer" :disabled="submitting || !userSql.trim()">
                {{ submitting ? '判题中...' : '提交答案' }}
              </button>
            </div>
            <div v-if="submitResult" class="result-panel" :class="{ correct: submitResult.is_correct, wrong: !submitResult.is_correct }">
              <div class="result-header">
                <span class="result-status">{{ submitResult.is_correct ? '✓ 正确' : '✗ 错误' }}</span>
                <span class="result-score">得分：{{ submitResult.score }}/100</span>
              </div>
              <div v-if="submitResult.feedback" class="result-feedback">
                <strong>反馈：</strong>
                <div class="markdown-content" v-html="renderMarkdown(submitResult.feedback)"></div>
              </div>
            </div>
            <div v-if="recommendations.length > 0" class="recommendations-panel">
              <div class="rec-header">
                <span class="rec-icon">💡</span>
                <span class="rec-title">智能推荐</span>
              </div>
              <div class="rec-cards">
                <div
                  v-for="(rec, idx) in recommendations"
                  :key="idx"
                  class="rec-card"
                  :class="rec.type"
                  @click="handleRecClick(rec)"
                >
                  <div class="rec-card-type">
                    <span v-if="rec.type === 'knowledge'" class="type-badge knowledge">📖 知识点</span>
                    <span v-else class="type-badge practice">✏️ 继续做题</span>
                  </div>
                  <div class="rec-card-title">{{ rec.title }}</div>
                  <div v-if="rec.chapter" class="rec-card-chapter">{{ rec.chapter }}</div>
                  <div class="rec-card-reason">{{ rec.reason }}</div>
                  <div class="rec-card-action">
                    <span v-if="rec.type === 'knowledge'">查看知识点 →</span>
                    <span v-else>开始做题 →</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="card empty-editor">
            <div class="empty-icon">✏️</div>
            <h3>选择一道题目开始练习</h3>
            <p>从左侧列表中选择SQL练习题</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { sqlApi, type SqlQuestion, type SqlSubmitResult, type SqlPracticeRecommendation } from '../api'
import { marked } from 'marked'

const router = useRouter()
const questions = ref<SqlQuestion[]>([])
const selectedQuestion = ref<SqlQuestion | null>(null)
const userSql = ref('')
const filterChapter = ref('')
const filterDifficulty = ref('')
const submitting = ref(false)
const submitResult = ref<SqlSubmitResult | null>(null)
const recommendations = ref<SqlPracticeRecommendation[]>([])

onMounted(() => {
  loadQuestions()
})

async function loadQuestions() {
  const { data } = await sqlApi.listQuestions(filterChapter.value || undefined, filterDifficulty.value || undefined)
  questions.value = data
}

function selectQuestion(q: SqlQuestion) {
  selectedQuestion.value = q
  userSql.value = ''
  submitResult.value = null
  recommendations.value = []
}

async function submitAnswer() {
  if (!selectedQuestion.value || !userSql.value.trim()) return
  submitting.value = true
  submitResult.value = null
  recommendations.value = []
  try {
    const { data } = await sqlApi.submit(selectedQuestion.value.id, userSql.value)
    submitResult.value = data
    recommendations.value = data.recommendations || []
  } catch (e) {
    submitResult.value = {
      id: '',
      question_id: selectedQuestion.value.id,
      user_sql: userSql.value,
      is_correct: false,
      score: 0,
      feedback: '提交失败，请稍后重试',
      execution_result: null,
      created_at: new Date().toISOString(),
    }
    recommendations.value = []
  } finally {
    submitting.value = false
  }
}

function handleRecClick(rec: SqlPracticeRecommendation) {
  if (rec.type === 'knowledge' && rec.node_id) {
    router.push({ path: '/knowledge-tree', query: { nodeId: rec.node_id } })
  } else if (rec.type === 'practice' && rec.question_id) {
    const q = questions.value.find(q => q.id === rec.question_id)
    if (q) {
      selectQuestion(q)
    } else {
      loadAndSelectQuestion(rec.question_id)
    }
  }
}

async function loadAndSelectQuestion(questionId: string) {
  try {
    const { data } = await sqlApi.getQuestion(questionId)
    selectedQuestion.value = data
    userSql.value = ''
    submitResult.value = null
    recommendations.value = []
  } catch (e) {
    console.error('加载题目失败:', e)
  }
}

function formatSql() {
  userSql.value = userSql.value
    .replace(/\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|ORDER BY|GROUP BY|HAVING|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|ALTER|DROP|INDEX|VIEW)\b/gi,
      (match) => match.toUpperCase())
    .replace(/\s+/g, ' ')
    .trim()
}

function clearEditor() {
  userSql.value = ''
  submitResult.value = null
  recommendations.value = []
}

function difficultyLabel(d: string): string {
  const map: Record<string, string> = { easy: '简单', medium: '中等', hard: '困难' }
  return map[d] || d
}

function renderMarkdown(content: string): string {
  return marked.parse(content) as string
}
</script>

<style scoped>
.sql-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - var(--header-height) - 48px);
}

.question-panel {
  width: 320px;
  flex-shrink: 0;
}

.question-panel .card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.filter-bar select {
  flex: 1;
  padding: 6px 8px;
}

.question-list {
  flex: 1;
  overflow-y: auto;
}

.question-item {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.question-item:hover {
  border-color: var(--primary-light);
}

.question-item.active {
  border-color: var(--primary);
  background: #eef4fd;
}

.question-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}

.question-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.chapter-tag {
  color: var(--text-secondary);
}

.difficulty-tag {
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.difficulty-tag.easy { background: #dcfce7; color: #166534; }
.difficulty-tag.medium { background: #fef3c7; color: #92400e; }
.difficulty-tag.hard { background: #fee2e2; color: #991b1b; }

.editor-panel {
  flex: 1;
}

.editor-panel .card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.question-detail-title {
  font-size: 16px;
  margin-bottom: 8px;
}

.question-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  line-height: 1.6;
}

.question-hint {
  background: #fef3c7;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 16px;
}

.sql-editor {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  min-height: 200px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  font-weight: 500;
}

.editor-actions {
  display: flex;
  gap: 6px;
}

.editor-actions .btn {
  padding: 4px 10px;
  font-size: 12px;
}

.sql-textarea {
  flex: 1;
  border: none;
  padding: 12px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
  outline: none;
  min-height: 160px;
}

.submit-bar {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.result-panel {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid;
}

.result-panel.correct {
  background: #f0fdf4;
  border-color: #86efac;
}

.result-panel.wrong {
  background: #fef2f2;
  border-color: #fca5a5;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-status {
  font-weight: 600;
  font-size: 15px;
}

.result-score {
  font-size: 14px;
  color: var(--text-secondary);
}

.result-feedback {
  font-size: 14px;
  line-height: 1.6;
}

.recommendations-panel {
  margin-top: 16px;
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.rec-icon {
  font-size: 18px;
}

.rec-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.rec-card {
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  background: white;
}

.rec-card:hover {
  border-color: var(--primary-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.rec-card.knowledge {
  border-left: 3px solid #3b82f6;
}

.rec-card.practice {
  border-left: 3px solid #10b981;
}

.rec-card-type {
  margin-bottom: 6px;
}

.type-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.type-badge.knowledge {
  background: #eff6ff;
  color: #1d4ed8;
}

.type-badge.practice {
  background: #ecfdf5;
  color: #047857;
}

.rec-card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 4px;
}

.rec-card-chapter {
  font-size: 11px;
  color: var(--primary);
  margin-bottom: 4px;
}

.rec-card-reason {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 6px;
}

.rec-card-action {
  font-size: 12px;
  color: var(--primary);
  font-weight: 500;
}

.empty-editor {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

.empty-editor .empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-hint {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
