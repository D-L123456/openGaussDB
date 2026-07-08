<template>
  <div class="profile-view">
    <div class="profile-header">
      <h2>学习画像</h2>
      <button class="btn btn-primary" @click="refreshDashboard" :disabled="store.loading">刷新分析</button>
    </div>

    <div v-if="store.loading" class="loading">加载中...</div>

    <template v-else>
      <div class="profile-grid">
        <div class="profile-card radar-card">
          <h3>能力雷达图</h3>
          <svg viewBox="0 0 300 300" class="radar-svg">
            <polygon v-for="r in [80, 60, 40, 20]" :key="r" :points="radarGrid(r)" fill="none" stroke="#e2e8f0" stroke-width="1"/>
            <line v-for="i in 8" :key="'l'+i" :x1="150" :y1="150" :x2="radarPoint(i, 80).x" :y2="radarPoint(i, 80).y" stroke="#e2e8f0" stroke-width="1"/>
            <polygon :points="radarArea()" fill="rgba(59,130,246,0.2)" stroke="#3b82f6" stroke-width="2"/>
            <circle v-for="i in 8" :key="'d'+i" :cx="radarPoint(i, store.abilityScores[i-1] * 0.8).x" :cy="radarPoint(i, store.abilityScores[i-1] * 0.8).y" r="4" fill="#3b82f6"/>
            <text v-for="(dim, i) in store.ABILITY_DIMS" :key="'t'+i" :x="radarPoint(i+1, 95).x" :y="radarPoint(i+1, 95).y" text-anchor="middle" fill="#374151" font-size="9" font-weight="500">{{ dim }}</text>
          </svg>
          <div class="score-summary">
            <span class="score-label">综合评分</span>
            <span class="score-value">{{ store.abilityScore }} / 100</span>
          </div>
        </div>

        <div class="profile-card stats-card">
          <h3>学习统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ formatTime(store.profile?.total_learning_time || 0) }}</div>
              <div class="stat-label">累计学习</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ store.profile?.streak_days || 0 }}天</div>
              <div class="stat-label">连续学习</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ store.completedLevels.size }}</div>
              <div class="stat-label">通关数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ store.badges.length }}</div>
              <div class="stat-label">徽章数</div>
            </div>
          </div>

          <div class="style-section">
            <span class="style-label">学习风格：</span>
            <span class="style-badge">{{ styleName }}</span>
          </div>

          <div v-if="store.badges.length" class="badges-section">
            <h4>获得徽章</h4>
            <div class="badges-list">
              <span v-for="b in store.badges" :key="b.key" class="badge-item">{{ b.name }}</span>
            </div>
          </div>
        </div>

        <div class="profile-card weak-card">
          <h3>薄弱环节</h3>
          <div v-if="store.weakPoints.length === 0" class="empty-text">暂无明显薄弱环节，继续保持！</div>
          <div v-else class="weak-list">
            <div v-for="w in store.weakPoints.slice(0, 5)" :key="w.category" class="weak-item">
              <div class="weak-header">
                <span class="weak-category">{{ w.category }}</span>
                <span class="weak-count">{{ w.count }}次</span>
              </div>
              <div class="weak-bar-bg">
                <div class="weak-bar" :style="{ width: Math.min(w.count * 20, 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="profile-card growth-card">
          <h3>能力成长曲线</h3>
          <div v-if="abilityHistory.length < 2" class="empty-text">完成更多关卡后将展示成长曲线</div>
          <svg v-else viewBox="0 0 500 200" class="growth-svg">
            <line v-for="i in 5" :key="'g'+i" :x1="40" :y1="10 + (i-1) * 45" :x2="480" :y2="10 + (i-1) * 45" stroke="#f1f5f9" stroke-width="1"/>
            <text v-for="i in 5" :key="'gt'+i" x="35" :y="14 + (i-1) * 45" text-anchor="end" fill="#94a3b8" font-size="9">{{ 100 - (i-1) * 25 }}</text>
            <polyline v-for="(_dim, di) in store.ABILITY_DIMS" :key="'c'+di" :points="growthLine(di)" fill="none" :stroke="dimColors[di]" stroke-width="1.5" opacity="0.7"/>
            <text v-for="(_dim, di) in store.ABILITY_DIMS" :key="'dl'+di" :x="485" :y="growthLastY(di)" fill="#64748b" font-size="7">{{ store.ABILITY_DIMS[di].slice(0, 4) }}</text>
          </svg>
        </div>

        <div class="profile-card recommend-card">
          <h3>智能推荐</h3>
          <div v-if="store.recommendations.length === 0" class="empty-text">暂无推荐，开始学习后将获得个性化建议</div>
          <div v-else class="rec-list">
            <div v-for="r in store.recommendations.slice(0, 5)" :key="r.id" class="rec-item" @click="handleRecAction(r)">
              <div class="rec-type-badge" :class="r.rec_type">{{ recTypeName(r.rec_type) }}</div>
              <div class="rec-content">
                <div class="rec-title">{{ r.title }}</div>
                <div class="rec-desc">{{ r.description }}</div>
              </div>
              <div class="rec-priority" :class="'p' + r.priority">P{{ r.priority }}</div>
            </div>
          </div>
        </div>

        <div class="profile-card timeline-card">
          <h3>学习时间线</h3>
          <div v-if="timeline.length === 0" class="empty-text">暂无学习记录</div>
          <div v-else class="timeline-list">
            <div v-for="t in timeline.slice(0, 15)" :key="t.id" class="timeline-item">
              <div class="timeline-dot" :class="t.event_type"></div>
              <div class="timeline-content">
                <div class="timeline-title">{{ eventLabel(t) }}</div>
                <div class="timeline-time">{{ formatTime2(t.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="profile-card error-card">
          <h3>错误热力图</h3>
          <div v-if="errorPatterns.length === 0" class="empty-text">暂无错误记录</div>
          <div v-else class="error-list">
            <div v-for="p in errorPatterns.slice(0, 8)" :key="p.id" class="error-item" :style="{ opacity: 0.4 + 0.6 * (p.occurrence_count / maxErrorCount) }">
              <span class="error-cat">{{ p.category }}</span>
              <span class="error-count">{{ p.occurrence_count }}次</span>
              <span v-if="p.ability_dim" class="error-dim">{{ p.ability_dim }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLearningStore } from '../stores/learning'
import { learningApi } from '../api'
import type { LearningRecommendation } from '../api'

const store = useLearningStore()
const router = useRouter()

const abilityHistory = computed(() => store.dashboard?.ability_history || [])
const timeline = computed(() => store.dashboard?.timeline || [])
const errorPatterns = computed(() => store.dashboard?.top_error_patterns || [])

const maxErrorCount = computed(() => {
  const patterns = errorPatterns.value
  if (!patterns.length) return 1
  return Math.max(...patterns.map(p => p.occurrence_count))
})

const styleName = computed(() => {
  const s = store.profile?.learning_style
  if (s === 'explorer') return '探索型'
  if (s === 'theorist') return '理论型'
  if (s === 'practitioner') return '实践型'
  return '待定'
})

const dimColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function radarPoint(index: number, radius: number) {
  const angle = (Math.PI * 2 * (index - 1)) / 8 - Math.PI / 2
  return { x: 150 + radius * Math.cos(angle), y: 150 + radius * Math.sin(angle) }
}

function radarGrid(radius: number) {
  return Array.from({ length: 8 }, (_, i) => {
    const p = radarPoint(i + 1, radius)
    return `${p.x},${p.y}`
  }).join(' ')
}

function radarArea() {
  return Array.from({ length: 8 }, (_, i) => {
    const p = radarPoint(i + 1, store.abilityScores[i] * 0.8)
    return `${p.x},${p.y}`
  }).join(' ')
}

function growthLine(dimIndex: number) {
  const history = abilityHistory.value
  if (history.length < 2) return ''
  const dims = store.ABILITY_DIMS
  const dim = dims[dimIndex]
  const points = history.map((s, i) => {
    const x = 40 + (i / (history.length - 1)) * 440
    const val = (s.ability_scores as Record<string, number>)?.[dim] ?? 10
    const y = 190 - (val / 100) * 180
    return `${x},${y}`
  })
  return points.join(' ')
}

function growthLastY(dimIndex: number) {
  const history = abilityHistory.value
  if (!history.length) return 0
  const last = history[history.length - 1]
  const dim = store.ABILITY_DIMS[dimIndex]
  const val = (last.ability_scores as Record<string, number>)?.[dim] ?? 10
  return 190 - (val / 100) * 180 + 3
}

function formatTime(seconds: number) {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  return `${(seconds / 3600).toFixed(1)}小时`
}

function formatTime2(iso: string | null) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
}

function eventLabel(t: Record<string, any>) {
  const type = t.event_type
  if (type === 'challenge_pass') return `通关第${t.level}关`
  if (type === 'challenge_error') return `第${t.level}关出错`
  if (type === 'challenge_start') return `开始第${t.level}关`
  if (type === 'challenge_submit') return `提交第${t.level}关`
  if (type === 'sql_submit') return '提交SQL练习'
  if (type === 'sql_error') return 'SQL练习出错'
  if (type === 'sql_pass') return 'SQL练习通过'
  if (type === 'chat_ask') return '知识问答'
  if (type === 'knowledge_browse') return '浏览知识树'
  return type
}

function recTypeName(type: string) {
  if (type === 'knowledge') return '学知识'
  if (type === 'practice') return '做练习'
  if (type === 'challenge') return '闯关'
  if (type === 'review') return '复习'
  return type
}

function handleRecAction(r: LearningRecommendation) {
  if (r.action_type === 'goto_challenge' && r.action_target) {
    router.push('/challenge')
  } else if (r.action_type === 'goto_knowledge') {
    router.push('/knowledge-tree')
  } else if (r.action_type === 'goto_sql') {
    router.push('/sql-practice')
  }
}

async function refreshDashboard() {
  await learningApi.getRecommendations(true)
  await store.fetchDashboard()
}

onMounted(() => {
  store.fetchDashboard()
})
</script>

<style scoped>
.profile-view { padding: 24px; max-width: 1200px; margin: 0 auto; }
.profile-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.profile-header h2 { font-size: 22px; font-weight: 700; color: #1e293b; margin: 0; }
.loading { text-align: center; padding: 60px; color: #64748b; }

.profile-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.profile-card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
.profile-card h3 { font-size: 16px; font-weight: 600; color: #1e293b; margin: 0 0 16px 0; }

.radar-card { text-align: center; }
.radar-svg { width: 280px; height: 280px; }
.score-summary { margin-top: 12px; }
.score-label { font-size: 13px; color: #64748b; }
.score-value { font-size: 20px; font-weight: 700; color: #3b82f6; margin-left: 8px; }

.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-item { text-align: center; padding: 12px; background: #f8fafc; border-radius: 8px; }
.stat-value { font-size: 20px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 12px; color: #64748b; margin-top: 4px; }

.style-section { margin-bottom: 16px; }
.style-label { font-size: 13px; color: #64748b; }
.style-badge { font-size: 13px; font-weight: 600; color: #8b5cf6; background: #f5f3ff; padding: 2px 10px; border-radius: 12px; }

.badges-section h4 { font-size: 13px; color: #64748b; margin: 0 0 8px 0; }
.badges-list { display: flex; flex-wrap: wrap; gap: 8px; }
.badge-item { font-size: 12px; background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 12px; font-weight: 500; }

.weak-list { display: flex; flex-direction: column; gap: 12px; }
.weak-item { }
.weak-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
.weak-category { font-size: 13px; color: #374151; font-weight: 500; }
.weak-count { font-size: 12px; color: #ef4444; font-weight: 600; }
.weak-bar-bg { height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.weak-bar { height: 100%; background: linear-gradient(90deg, #f59e0b, #ef4444); border-radius: 3px; transition: width 0.3s; }

.growth-svg { width: 100%; height: 180px; }
.recommend-card { grid-column: span 2; }
.rec-list { display: flex; flex-direction: column; gap: 10px; }
.rec-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8fafc; border-radius: 8px; cursor: pointer; transition: background 0.2s; }
.rec-item:hover { background: #f0f7ff; }
.rec-type-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; white-space: nowrap; }
.rec-type-badge.knowledge { background: #dbeafe; color: #1d4ed8; }
.rec-type-badge.practice { background: #d1fae5; color: #047857; }
.rec-type-badge.challenge { background: #fef3c7; color: #92400e; }
.rec-type-badge.review { background: #fce7f3; color: #9d174d; }
.rec-content { flex: 1; min-width: 0; }
.rec-title { font-size: 14px; font-weight: 600; color: #1e293b; }
.rec-desc { font-size: 12px; color: #64748b; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rec-priority { font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
.rec-priority.p1 { background: #fef2f2; color: #dc2626; }
.rec-priority.p2 { background: #fff7ed; color: #ea580c; }
.rec-priority.p3 { background: #fefce8; color: #ca8a04; }
.rec-priority.p4, .rec-priority.p5 { background: #f1f5f9; color: #64748b; }

.timeline-card { }
.timeline-list { max-height: 300px; overflow-y: auto; }
.timeline-item { display: flex; align-items: center; gap: 10px; padding: 6px 0; border-bottom: 1px solid #f1f5f9; }
.timeline-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.timeline-dot.challenge_pass { background: #10b981; }
.timeline-dot.challenge_error { background: #ef4444; }
.timeline-dot.challenge_start, .timeline-dot.challenge_submit { background: #3b82f6; }
.timeline-dot.sql_pass { background: #10b981; }
.timeline-dot.sql_error, .timeline-dot.sql_submit { background: #f59e0b; }
.timeline-dot.chat_ask { background: #8b5cf6; }
.timeline-dot.knowledge_browse { background: #06b6d4; }
.timeline-content { flex: 1; }
.timeline-title { font-size: 13px; color: #374151; }
.timeline-time { font-size: 11px; color: #94a3b8; }

.error-card { }
.error-list { display: flex; flex-direction: column; gap: 8px; }
.error-item { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #fef2f2; border-radius: 8px; border-left: 3px solid #ef4444; }
.error-cat { font-size: 13px; font-weight: 500; color: #374151; flex: 1; }
.error-count { font-size: 12px; font-weight: 600; color: #ef4444; }
.error-dim { font-size: 11px; color: #64748b; background: #f1f5f9; padding: 1px 6px; border-radius: 8px; }

.empty-text { font-size: 13px; color: #94a3b8; text-align: center; padding: 24px; }

@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; }
  .recommend-card { grid-column: span 1; }
}
</style>