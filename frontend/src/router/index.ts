import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: () => import('../views/ChatView.vue'),
    },
    {
      path: '/sql-practice',
      name: 'sql-practice',
      component: () => import('../views/SqlPracticeView.vue'),
    },
    {
      path: '/knowledge-tree',
      name: 'knowledge-tree',
      component: () => import('../views/KnowledgeTreeView.vue'),
    },
    {
      path: '/challenge',
      name: 'challenge',
      component: () => import('../views/ChallengeView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
    },
  ],
})

export default router