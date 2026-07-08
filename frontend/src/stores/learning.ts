import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { learningApi, type UserProfile, type LearningRecommendation, type LearningDashboard } from '../api'

const ABILITY_DIMS = [
  '基础环境搭建',
  'openGauss运维',
  '数据库迁移与同步',
  '数据库开发',
  '数据库设计',
  '数据库优化与调优',
  'SQL编程与优化',
  '数据库对象管理',
]

export const useLearningStore = defineStore('learning', () => {
  const profile = ref<UserProfile | null>(null)
  const recommendations = ref<LearningRecommendation[]>([])
  const dashboard = ref<LearningDashboard | null>(null)
  const loading = ref(false)

  const abilityScores = computed(() => {
    if (!profile.value) return ABILITY_DIMS.map(() => 10)
    return ABILITY_DIMS.map(dim => (profile.value!.ability_scores as Record<string, number>)?.[dim] ?? 10)
  })

  const abilityScore = computed(() => {
    const scores = abilityScores.value
    return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
  })

  const weakPoints = computed(() => {
    if (!profile.value?.weak_points) return []
    return Object.entries(profile.value.weak_points as Record<string, any>)
      .map(([key, val]) => ({ category: key, ...val }))
      .sort((a: any, b: any) => (b.count || 0) - (a.count || 0))
  })

  const completedLevels = computed(() => {
    if (!profile.value?.challenge_progress) return new Set<number>()
    const progress = profile.value.challenge_progress as Record<string, any>
    const completed = new Set<number>()
    for (const [key, val] of Object.entries(progress)) {
      if ((val as any)?.status === 'passed') completed.add(Number(key))
    }
    return completed
  })

  const badges = computed(() => {
    if (!profile.value?.badges) return []
    const badgeMap: Record<string, string> = {
      first_clear: '初出茅庐',
      double_clear: '双关斩将',
      perfect_clear: '完美通关',
      streak_3: '三日坚持',
      streak_7: '七日达人',
      hour_scholar: '一小时学者',
    }
    return Object.entries(profile.value.badges as Record<string, boolean>)
      .filter(([, v]) => v)
      .map(([k]) => ({ key: k, name: badgeMap[k] || k }))
  })

  async function fetchProfile() {
    try {
      const res = await learningApi.getProfile()
      profile.value = res.data
    } catch (e) {
      console.error('Failed to fetch profile:', e)
    }
  }

  async function fetchRecommendations(refresh = false) {
    try {
      const res = await learningApi.getRecommendations(refresh)
      recommendations.value = res.data
    } catch (e) {
      console.error('Failed to fetch recommendations:', e)
    }
  }

  async function fetchDashboard() {
    loading.value = true
    try {
      const res = await learningApi.getDashboard()
      dashboard.value = res.data
      profile.value = res.data.profile
      recommendations.value = res.data.recent_recommendations
    } catch (e) {
      console.error('Failed to fetch dashboard:', e)
    } finally {
      loading.value = false
    }
  }

  async function recordEvent(
    eventType: string,
    level?: number,
    part?: number,
    detail?: Record<string, any>,
    durationSeconds?: number,
  ) {
    try {
      await learningApi.recordEvent({
        event_type: eventType,
        level,
        part,
        detail,
        duration_seconds: durationSeconds,
      })
    } catch (e) {
      console.error('Failed to record event:', e)
    }
  }

  return {
    profile,
    recommendations,
    dashboard,
    loading,
    abilityScores,
    abilityScore,
    weakPoints,
    completedLevels,
    badges,
    ABILITY_DIMS,
    fetchProfile,
    fetchRecommendations,
    fetchDashboard,
    recordEvent,
  }
})