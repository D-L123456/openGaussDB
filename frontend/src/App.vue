<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">OG</div>
        <h1>OpenGauss 智能体</h1>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <span class="nav-icon">💬</span>
          <span>知识问答</span>
        </router-link>
        <router-link to="/sql-practice" class="nav-item" :class="{ active: $route.path === '/sql-practice' }">
          <span class="nav-icon">✏️</span>
          <span>SQL练习</span>
        </router-link>
        <router-link to="/knowledge-tree" class="nav-item" :class="{ active: $route.path === '/knowledge-tree' }">
          <span class="nav-icon">🌳</span>
          <span>知识体系</span>
        </router-link>
        <router-link to="/challenge" class="nav-item" :class="{ active: $route.path === '/challenge' }">
          <span class="nav-icon">⚔️</span>
          <span>勇闯数据库</span>
        </router-link>
        <router-link to="/profile" class="nav-item" :class="{ active: $route.path === '/profile' }">
          <span class="nav-icon">📊</span>
          <span>学习画像</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>