<template>
  <div class="knowledge-tree-view">
    <div class="header">知识树浏览</div>
    <div class="content-area">
      <div class="tree-layout">
        <div class="tree-panel card">
          <div class="tree-header">
            <h3>OpenGauss 知识体系</h3>
            <div class="tree-stats">
              <span>{{ stats.totalDocuments }} 个知识块</span>
              <span>{{ stats.chapters }} 个章节</span>
            </div>
          </div>
          <div class="tree-search">
            <input
              v-model="searchQuery"
              placeholder="搜索知识点..."
              @keydown.enter="searchKnowledge"
            />
            <button class="btn btn-primary" @click="searchKnowledge">搜索</button>
          </div>
          <div v-if="searchResults.length > 0" class="search-results">
            <div class="search-results-header">
              <span>搜索结果</span>
              <button class="btn btn-sm" @click="clearSearch">清除</button>
            </div>
            <div
              v-for="(result, idx) in searchResults"
              :key="idx"
              class="search-result-item"
            >
              <div class="result-chapter">{{ result.chapter }} > {{ result.section }}</div>
              <div class="result-title">{{ result.title }}</div>
              <div class="result-content">{{ result.content.slice(0, 150) }}...</div>
              <div class="result-score">相关度：{{ (result.score * 100).toFixed(1) }}%</div>
            </div>
          </div>
          <div v-else class="tree-content">
            <tree-node
              v-for="node in treeData"
              :key="node.id"
              :node="node"
              :depth="0"
              :selected-id="selectedNode?.id"
              :recommended-ids="recommendedIds"
              @select="selectNode"
            />
          </div>
        </div>
        <div class="detail-panel card">
          <div v-if="selectedNode" class="node-detail">
            <div class="detail-header">
              <h2 class="detail-title">{{ selectedNode.title }}</h2>
              <div class="node-breadcrumb">
                <span v-for="(crumb, idx) in breadcrumbs" :key="idx">
                  <span class="crumb">{{ crumb }}</span>
                  <span v-if="idx < breadcrumbs.length - 1" class="crumb-sep">/</span>
                </span>
              </div>
            </div>
            <div v-if="selectedNode.content" class="node-content markdown-body" v-html="renderMarkdown(selectedNode.content)"></div>
            <div v-else class="no-content">
              <div class="no-content-icon">📄</div>
              <p>该节点暂无详细内容</p>
              <p class="hint">请点击子节点查看具体知识点</p>
            </div>
          </div>
          <div v-else class="empty-detail">
            <div class="empty-icon">📖</div>
            <h3>选择知识点查看详情</h3>
            <p>从左侧知识树中选择一个节点</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { knowledgeApi, type KnowledgeNode } from '../api'
import { marked } from 'marked'
import TreeNode from '../components/TreeNode.vue'

const route = useRoute()
const treeData = ref<KnowledgeNode[]>([])
const selectedNode = ref<KnowledgeNode | null>(null)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const stats = ref({ totalDocuments: 0, chapters: 0 })
const recommendedIds = ref<Set<string>>(new Set())

const breadcrumbs = computed(() => {
  if (!selectedNode.value) return []
  const parts: string[] = []
  if (selectedNode.value.chapter) parts.push(selectedNode.value.chapter)
  if (selectedNode.value.section) {
    const sections = selectedNode.value.section.split(' > ')
    parts.push(...sections)
  }
  return [...new Set(parts)]
})

onMounted(async () => {
  await loadTree()
  await loadStats()
  const nodeId = route.query.nodeId as string | undefined
  if (nodeId) {
    recommendedIds.value = new Set([nodeId])
    autoSelectNode(nodeId, treeData.value)
  }
})

async function loadTree() {
  const { data } = await knowledgeApi.getTree()
  treeData.value = data.nodes
}

async function loadStats() {
  const { data } = await knowledgeApi.getStats()
  stats.value = data
}

async function searchKnowledge() {
  if (!searchQuery.value.trim()) return
  const { data } = await knowledgeApi.search(searchQuery.value)
  searchResults.value = data
}

function clearSearch() {
  searchQuery.value = ''
  searchResults.value = []
}

function selectNode(node: KnowledgeNode) {
  selectedNode.value = node
  searchResults.value = []
}

function autoSelectNode(nodeId: string, nodes: KnowledgeNode[]): boolean {
  for (const node of nodes) {
    if (node.id === nodeId) {
      selectedNode.value = node
      return true
    }
    if (node.children?.length) {
      if (autoSelectNode(nodeId, node.children)) return true
    }
  }
  return false
}

function renderMarkdown(content: string): string {
  return marked.parse(content) as string
}
</script>

<style scoped>
.tree-layout {
  display: flex;
  gap: 24px;
  height: calc(100vh - var(--header-height) - 48px);
}

.tree-panel {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tree-header {
  margin-bottom: 16px;
}

.tree-header h3 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text);
}

.tree-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.tree-search {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tree-search input {
  flex: 1;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.search-results {
  flex: 1;
  overflow-y: auto;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.btn-sm {
  padding: 2px 8px;
  font-size: 12px;
}

.search-result-item {
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

.search-result-item:hover {
  border-color: var(--primary-light);
  background: #fafbfd;
}

.result-chapter {
  font-size: 11px;
  color: var(--primary);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.result-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}

.result-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 6px;
}

.result-score {
  font-size: 11px;
  color: var(--text-secondary);
}

.detail-panel {
  flex: 1;
  overflow-y: auto;
  padding: 32px 40px;
}

.detail-header {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.detail-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text);
  line-height: 1.3;
}

.node-breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 13px;
}

.crumb {
  color: var(--primary);
}

.crumb-sep {
  color: var(--text-secondary);
  margin: 0 2px;
}

.node-content {
  font-size: 15px;
  line-height: 1.9;
  color: #374151;
  max-width: 780px;
}

.no-content {
  color: var(--text-secondary);
  text-align: center;
  padding: 60px 20px;
}

.no-content-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.hint {
  font-size: 13px;
  margin-top: 8px;
  color: var(--text-secondary);
}

.empty-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
}

.empty-detail .empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-detail h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: var(--text);
}

.empty-detail p {
  font-size: 14px;
}
</style>

<style>
.markdown-body h1 {
  font-size: 22px;
  font-weight: 700;
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--border);
  color: var(--text);
}

.markdown-body h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 28px 0 14px;
  color: var(--text);
}

.markdown-body h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 24px 0 12px;
  color: var(--text);
}

.markdown-body h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 20px 0 10px;
  color: var(--text);
}

.markdown-body p {
  margin-bottom: 14px;
  line-height: 1.9;
}

.markdown-body ul, .markdown-body ol {
  padding-left: 24px;
  margin-bottom: 14px;
}

.markdown-body li {
  margin-bottom: 6px;
  line-height: 1.8;
}

.markdown-body pre {
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 20px;
  overflow-x: auto;
  margin: 16px 0;
  line-height: 1.7;
}

.markdown-body code {
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
}

.markdown-body :not(pre) > code {
  background: #eff6ff;
  color: var(--primary-dark);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.markdown-body pre code {
  color: #1e293b;
}

.markdown-body blockquote {
  border-left: 4px solid var(--primary);
  padding: 12px 20px;
  margin: 16px 0;
  background: #f0f7ff;
  border-radius: 0 8px 8px 0;
  color: #374151;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
  font-size: 14px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.markdown-body th {
  background: #f1f5f9;
  font-weight: 600;
  text-align: left;
  padding: 10px 14px;
  border-bottom: 2px solid var(--border);
}

.markdown-body td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
}

.markdown-body tr:last-child td {
  border-bottom: none;
}

.markdown-body tr:hover td {
  background: #fafbfd;
}

.markdown-body hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}

.markdown-body strong {
  font-weight: 600;
  color: var(--text);
}

.markdown-body a {
  color: var(--primary);
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  border: 1px solid var(--border);
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
</style>
