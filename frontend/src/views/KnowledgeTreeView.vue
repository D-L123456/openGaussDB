<template>
  <div class="knowledge-tree-view">
    <div class="header">知识体系</div>
    <div class="content-area">
      <div class="tree-layout">
        <div class="tree-panel card">
          <div class="tree-header">
            <h3>OpenGauss 知识体系</h3>
            <div class="tree-stats">
              <span>{{ stats.total_documents }} 个知识块</span>
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
              :expanded-ids="expandedIds"
              @select="selectNode"
              @toggle-expand="toggleExpand"
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
            <div v-if="sectionQuiz" class="section-quiz-block">
              <div class="quiz-block-header">
                <span class="quiz-block-icon">✎</span>
                <span>本节检测</span>
                <span v-if="sectionQuizPassed" class="quiz-passed-badge">已通过</span>
              </div>
              <div v-if="!sectionQuizPassed" class="quiz-block-body">
                <div class="quiz-q-item" v-for="(q, qi) in sectionQuiz.questions" :key="qi">
                  <div class="quiz-q-header">
                    <span class="quiz-q-num">第{{ qi + 1 }}题</span>
                    <span class="quiz-q-type">{{ q.type === 'single' ? '单选' : q.type === 'multi' ? '多选' : q.type === 'judge' ? '判断' : '填空' }}</span>
                  </div>
                  <div class="quiz-q-text">{{ q.question }}</div>
                  <div v-if="q.type !== 'fill'" class="quiz-q-options">
                    <label v-for="(opt, oi) in q.options" :key="oi" class="quiz-q-option"
                      :class="{ selected: quizAnswers[qi] === opt || (Array.isArray(quizAnswers[qi]) && (quizAnswers[qi] as string[]).includes(opt)) }">
                      <input v-if="q.type === 'multi'" type="checkbox" :value="opt"
                        :checked="Array.isArray(quizAnswers[qi]) && (quizAnswers[qi] as string[]).includes(opt)"
                        @change="toggleMultiAnswer(qi, opt)" />
                      <input v-else type="radio" :name="'sq-'+sectionQuizKey+'-'+qi" :value="opt"
                        :checked="quizAnswers[qi] === opt"
                        @change="quizAnswers[qi] = opt" />
                      <span>{{ opt }}</span>
                    </label>
                  </div>
                  <div v-else class="quiz-q-fill">
                    <input class="quiz-fill-input" v-model="quizAnswers[qi]" placeholder="输入答案" />
                  </div>
                  <div v-if="quizChecked[qi]" class="quiz-q-result" :class="{ correct: quizResults[qi], wrong: !quizResults[qi] }">
                    <span v-if="quizResults[qi]">正确</span>
                    <span v-else>错误，正确答案：{{ Array.isArray(sectionQuiz!.questions[qi].answer) ? (sectionQuiz!.questions[qi].answer as string[]).join('、') : sectionQuiz!.questions[qi].answer }}</span>
                  </div>
                </div>
                <button class="btn btn-primary quiz-submit-btn" @click="checkSectionQuiz">提交答案</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-detail">
            <div class="empty-icon">📖</div>
            <h3>选择知识点查看详情</h3>
            <p>从左侧知识体系中选择一个节点</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { knowledgeApi, type KnowledgeNode } from '../api'
import { marked } from 'marked'
import TreeNode from '../components/TreeNode.vue'

interface SectionQuizQuestion {
  type: 'single' | 'multi' | 'judge' | 'fill'
  question: string
  options?: string[]
  answer: string | string[]
}

interface SectionQuiz {
  questions: SectionQuizQuestion[]
}

const route = useRoute()
const treeData = ref<KnowledgeNode[]>([])
const selectedNode = ref<KnowledgeNode | null>(null)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const stats = ref({ total_documents: 0, chapters: 0 })
const recommendedIds = ref<Set<string>>(new Set())
const expandedIds = ref<Set<string>>(new Set())

const quizAnswers = reactive<Record<number, string | string[]>>({})
const quizChecked = reactive<Record<number, boolean>>({})
const quizResults = reactive<Record<number, boolean>>({})
const sectionQuizPassed = ref(false)

function toggleExpand(nodeId: string) {
  const s = new Set(expandedIds.value)
  if (s.has(nodeId)) s.delete(nodeId)
  else s.add(nodeId)
  expandedIds.value = s
}

const sectionQuizKey = computed(() => {
  if (!selectedNode.value) return ''
  const ch = (selectedNode.value.chapter || '').replace(/-已同步$/, '')
  const sec = selectedNode.value.section || ''
  return ch + '||' + sec
})

const sectionQuiz = computed<SectionQuiz | null>(() => {
  if (!selectedNode.value) return null
  const ch = (selectedNode.value.chapter || '').replace(/-已同步$/, '')
  const sec = selectedNode.value.section || ''
  return quizMap[ch + '||' + sec] || null
})

const quizMap: Record<string, SectionQuiz> = {
  '第1章 数据库概论||1.1  数据库技术概述': {
    questions: [
      { type: 'multi', question: '存放在数据库中数据的特点是：', options: ['A.永久存储', 'B.有组织', 'C.独立性', 'D.可共享'], answer: ['A.永久存储', 'B.有组织', 'C.独立性', 'D.可共享'] },
      { type: 'judge', question: '数据库应用程序可以不经过数据库管理系统而直接读取数据库文件', options: ['A.正确', 'B.错误'], answer: 'B.错误' },
      { type: 'multi', question: '属于数据库系统概念范围的组成部分有：', options: ['A.数据库管理系统', 'B.数据库', 'C.应用开发工具', 'D.应用程序'], answer: ['A.数据库管理系统', 'B.数据库', 'C.应用开发工具', 'D.应用程序'] },
    ],
  },
  '第1章 数据库概论||1.2  数据库技术发展史': {
    questions: [
      { type: 'multi', question: '数据管理发展经历了哪几个阶段：', options: ['A.人工阶段', 'B.智能系统', 'C.文件系统', 'D.数据库系统'], answer: ['A.人工阶段', 'C.文件系统', 'D.数据库系统'] },
      { type: 'single', question: '允许一个以上节点无双亲，一个节点可以有多于一个的双亲，这是哪种数据模型：', options: ['A.层次模型', 'B.关系模型', 'C.面向对象模型', 'D.网状模型'], answer: 'D.网状模型' },
      { type: 'judge', question: 'NoSQL和NewSQL数据库的出现能够彻底颠覆和取代原有的关系型数据库系统', options: ['A.正确', 'B.错误'], answer: 'B.错误' },
    ],
  },
  '第1章 数据库概论||1.3  关系型数据库架构': {
    questions: [
      { type: 'judge', question: '主备架构可以通过读写分离方式来提高整体的读写并发能力', options: ['A.正确', 'B.错误'], answer: 'B.错误' },
      { type: 'single', question: '哪种数据库架构具有良好的线性扩展能力：', options: ['A.主从架构', 'B.Shared-Nothing架构', 'C.Shared-disk架构', 'D.主备架构'], answer: 'B.Shared-Nothing架构' },
      { type: 'judge', question: '分片架构的特点就是通过一定的算法把数据分散在集群的各个数据库节点上，利用集群内服务器数量的优势进行并行计算', options: ['A.正确', 'B.错误'], answer: 'A.正确' },
    ],
  },
  '第1章 数据库概论||1.4  关系型数据库主流应用场景': {
    questions: [
      { type: 'multi', question: '衡量OLTP系统的测试指标包括：', options: ['A.TPMC', 'B.Price/TPMC', 'C.QPHH', 'D.QPS'], answer: ['A.TPMC', 'B.Price/TPMC'] },
      { type: 'judge', question: 'OLAP系统能够对大量数据进行分析处理，所以同样能够满足OLTP对于小数据量处理性能需求', options: ['A.正确', 'B.错误'], answer: 'B.错误' },
    ],
  },
  '第2章 openGauss概述||2.1 初识openGauss': {
    questions: [
      { type: 'multi', question: '属于NoSQL数据库的是：', options: ['A.图数据库', 'B.文档数据库', 'C.键值数据库', 'D.列分组数据库'], answer: ['A.图数据库', 'B.文档数据库', 'C.键值数据库', 'D.列分组数据库'] },
      { type: 'single', question: 'openGauss的三权分立开启后，哪个管理员可以查看审计日志：', options: ['A.安全管理员', 'B.存储管理员', 'C.审计管理员', 'D.系统管理员'], answer: 'C.审计管理员' },
    ],
  },
  '第2章 openGauss概述||2.2 openGauss数据库安装与配置': {
    questions: [
      { type: 'single', question: 'WAL日志在openGauss中默认所在文件夹：', options: ['A.pg_log', 'B.pg_xlog', 'C.pg_audit', 'D.global'], answer: 'B.pg_xlog' },
      { type: 'single', question: '启动openGauss数据库服务的命令是：', options: ['A.gs_om start', 'B.start gs_om', 'C.gs_om -t start', 'D.start openGauss'], answer: 'C.gs_om -t start' },
      { type: 'single', question: '查询表空间信息的系统表是：', options: ['A.pg_tablespace', 'B.pg_tablespaces', 'C.dba_tablespace', 'D.dba_tablespaces'], answer: 'A.pg_tablespace' },
    ],
  },
  '第2章 openGauss概述||2.3 openGauss数据库管理': {
    questions: [
      { type: 'multi', question: '关于gs_dumpall命令描述正确的是：', options: ['A.由操作系统用户omm执行', 'B.导出时其他用户不能访问数据库', 'C.必须以管理员身份连接', 'D.导出结果为纯文本SQL脚本'], answer: ['A.由操作系统用户omm执行', 'C.必须以管理员身份连接', 'D.导出结果为纯文本SQL脚本'] },
      { type: 'fill', question: '创建数据库的SQL命令是____ DATABASE', answer: 'CREATE' },
    ],
  },
  '第2章 openGauss概述||2.4 openGauss数据库安全管理': {
    questions: [
      { type: 'multi', question: '关于用户与角色的区别和联系，描述正确的是：', options: ['A.角色是实体，用户是行为', 'B.用户可被赋予一个或多个角色', 'C.对用户权限的管理可简化为对角色权限的管理', 'D.用户和角色使用不同的操作方式与维护方式'], answer: ['B.用户可被赋予一个或多个角色', 'C.对用户权限的管理可简化为对角色权限的管理'] },
      { type: 'fill', question: '回收用户权限的SQL命令是____', answer: 'REVOKE' },
    ],
  },
  '第3章openGauss数据表管理||3.1 openGauss数据类型': {
    questions: [
      { type: 'single', question: 'openGauss几何类型中表示矩形的是：', options: ['A.point', 'B.lseg', 'C.box', 'D.polygon'], answer: 'C.box' },
      { type: 'single', question: '下列数据类型占用存储空间不是4个字节的是：', options: ['A.SERIAL', 'B.BIGSERIAL', 'C.REAL', 'D.FLOAT4'], answer: 'B.BIGSERIAL' },
      { type: 'single', question: 'openGauss网络地址数据类型中不可以存储：', options: ['A.IPv4', 'B.IPv6', 'C.IPv8'], answer: 'C.IPv8' },
    ],
  },
  '第3章openGauss数据表管理||3.2 数据表分类': {
    questions: [
      { type: 'single', question: '和列存模型相比，行存模型的优点是：', options: ['A.选择时只读取被选择的列', 'B.Insert/Update不容易', 'C.投影很高效', 'D.数据被保存在一起'], answer: 'D.数据被保存在一起' },
      { type: 'judge', question: '分区表可以将大表的数据分散到多个物理文件中，提高查询性能', options: ['A.正确', 'B.错误'], answer: 'A.正确' },
    ],
  },
  '第3章openGauss数据表管理||3.3 数据表管理': {
    questions: [
      { type: 'single', question: '用户无法向数据库中输入数据，可能是因为：', options: ['A.数据库过多', 'B.约束不起作用', 'C.数据行太多', 'D.还没有创建数据库表'], answer: 'D.还没有创建数据库表' },
      { type: 'single', question: '假设Course表是主表，Student表是子表，建立主外键关系应：', options: ['A.在设计Course表时进入关系设计', 'B.在设计Student表时进入关系设计', 'C.主键和外键名称必须一样', 'D.主键和外键必须是自动增长类型'], answer: 'B.在设计Student表时进入关系设计' },
      { type: 'fill', question: '主键用来实施____完整性', answer: '实体' },
    ],
  },
}

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
    expandAndSelectNode(nodeId, treeData.value)
  }
})

watch(() => route.query.nodeId, (newNodeId) => {
  if (newNodeId && treeData.value.length > 0) {
    const id = newNodeId as string
    recommendedIds.value = new Set([id])
    expandAndSelectNode(id, treeData.value)
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
  resetQuizState()
  loadQuizPassedState()
}

function expandAndSelectNode(nodeId: string, nodes: KnowledgeNode[]): boolean {
  for (const node of nodes) {
    if (node.id === nodeId) {
      selectedNode.value = node
      return true
    }
    if (node.children?.length) {
      if (expandAndSelectNode(nodeId, node.children)) {
        expandedIds.value = new Set([...expandedIds.value, node.id])
        return true
      }
    }
  }
  return false
}

function resetQuizState() {
  for (const k of Object.keys(quizAnswers)) delete quizAnswers[Number(k)]
  for (const k of Object.keys(quizChecked)) delete quizChecked[Number(k)]
  for (const k of Object.keys(quizResults)) delete quizResults[Number(k)]
  sectionQuizPassed.value = false
}

function loadQuizPassedState() {
  const key = sectionQuizKey.value
  try {
    const stored = localStorage.getItem('quiz_passed_' + key)
    sectionQuizPassed.value = stored === 'true'
  } catch { sectionQuizPassed.value = false }
}

function toggleMultiAnswer(qi: number, opt: string) {
  const current = (quizAnswers[qi] as string[]) || []
  if (current.includes(opt)) {
    quizAnswers[qi] = current.filter(o => o !== opt)
  } else {
    quizAnswers[qi] = [...current, opt]
  }
}

function checkSectionQuiz() {
  if (!sectionQuiz.value) return
  const questions = sectionQuiz.value.questions
  let allCorrect = true
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i]
    const userAns = quizAnswers[i]
    let correct = false
    if (q.type === 'multi') {
      const expected = (q.answer as string[]).slice().sort()
      const actual = ((userAns as string[]) || []).slice().sort()
      correct = JSON.stringify(expected) === JSON.stringify(actual)
    } else if (q.type === 'fill') {
      correct = (userAns as string || '').trim().toUpperCase() === (q.answer as string).toUpperCase()
    } else {
      correct = userAns === q.answer
    }
    quizChecked[i] = true
    quizResults[i] = correct
    if (!correct) allCorrect = false
  }
  if (allCorrect) {
    sectionQuizPassed.value = true
    try {
      localStorage.setItem('quiz_passed_' + sectionQuizKey.value, 'true')
    } catch {}
  }
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

.section-quiz-block {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid var(--border);
}

.quiz-block-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 20px;
}

.quiz-block-icon {
  font-size: 18px;
  color: var(--primary);
}

.quiz-passed-badge {
  font-size: 12px;
  font-weight: 600;
  color: #16a34a;
  background: #f0fdf4;
  border: 1px solid #86efac;
  padding: 2px 10px;
  border-radius: 12px;
}

.quiz-q-item {
  margin-bottom: 24px;
  padding: 16px;
  background: #fafbfc;
  border: 1px solid var(--border);
  border-radius: 10px;
}

.quiz-q-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.quiz-q-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
}

.quiz-q-type {
  font-size: 11px;
  color: var(--text-secondary);
  background: #f1f5f9;
  padding: 1px 8px;
  border-radius: 4px;
}

.quiz-q-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
  margin-bottom: 12px;
}

.quiz-q-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quiz-q-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}

.quiz-q-option:hover {
  background: #f8fafc;
}

.quiz-q-option.selected {
  background: #eff6ff;
  border-color: var(--primary);
  color: var(--primary);
  font-weight: 500;
}

.quiz-q-option input {
  accent-color: var(--primary);
}

.quiz-q-fill {
  margin-top: 4px;
}

.quiz-fill-input {
  width: 200px;
  padding: 6px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 14px;
}

.quiz-q-result {
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.quiz-q-result.correct {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #86efac;
}

.quiz-q-result.wrong {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fca5a5;
}

.quiz-submit-btn {
  margin-top: 16px;
  width: 100%;
  padding: 10px;
  font-size: 15px;
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
