<template>
  <div class="tree-node" :style="{ paddingLeft: depth * 12 + 'px' }">
    <div
      class="node-row"
      :class="{ selected: isSelected, recommended: isRecommended, read: isRead }"
      @click="toggle"
    >
      <span class="expand-icon" v-if="node.children?.length" @click.stop="toggleExpand">
        <svg :class="{ rotated: isExpanded }" width="10" height="10" viewBox="0 0 10 10">
          <path d="M3 1L7 5L3 9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </span>
      <span class="node-leaf-icon" v-else></span>
      <span class="node-title" :class="{ selected: isSelected, 'has-content': node.content }">{{ node.title }}</span>
      <span v-if="isRead && !isQuizNode" class="read-check" title="已阅读">✓</span>
      <span v-if="isRecommended" class="star-badge" title="智能推荐">★</span>
    </div>
    <div v-if="isExpanded && node.children?.length" class="node-children">
      <tree-node
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :depth="depth + 1"
        :selected-id="selectedId"
        :recommended-ids="recommendedIds"
        :expanded-ids="expandedIds"
        :read-node-ids="readNodeIds"
        @select="$emit('select', $event)"
        @toggle-expand="$emit('toggle-expand', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { KnowledgeNode } from '../api'

const props = defineProps<{
  node: KnowledgeNode
  depth: number
  selectedId?: string
  recommendedIds?: Set<string>
  expandedIds?: Set<string>
  readNodeIds?: Set<string>
}>()

const emit = defineEmits<{
  select: [node: KnowledgeNode]
  'toggle-expand': [nodeId: string]
}>()

const isExpanded = computed(() => {
  if (!props.expandedIds) return false
  return props.expandedIds.has(props.node.id)
})

const isSelected = computed(() => props.selectedId === props.node.id)

const isRecommended = computed(() => {
  if (!props.recommendedIds) return false
  return props.recommendedIds.has(props.node.id)
})

const isRead = computed(() => {
  if (!props.readNodeIds) return false
  return props.readNodeIds.has(props.node.id)
})

const isQuizNode = computed(() => props.node.id.startsWith('quiz-'))

function toggle() {
  if (props.node.children?.length) {
    emit('toggle-expand', props.node.id)
  }
  emit('select', props.node)
}

function toggleExpand() {
  emit('toggle-expand', props.node.id)
}
</script>

<style scoped>
.node-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
  user-select: none;
}

.node-row:hover {
  background: #f1f5f9;
}

.node-row.selected {
  background: #eff6ff;
}

.node-row.selected .node-title {
  color: var(--primary);
  font-weight: 500;
}

.node-row.recommended {
  background: #fffbeb;
  border: 1px solid #fbbf24;
}

.node-row.recommended .node-title {
  color: #92400e;
  font-weight: 500;
}

.node-row.read {
  background: #f0fdf4;
}

.node-row.read .node-title {
  color: #166534;
}

.expand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.expand-icon svg {
  transition: transform 0.2s;
}

.expand-icon svg.rotated {
  transform: rotate(90deg);
}

.node-leaf-icon {
  width: 4px;
  height: 4px;
  background: #cbd5e1;
  border-radius: 50%;
  margin: 0 6px;
  flex-shrink: 0;
}

.node-row.read .node-leaf-icon {
  background: #22c55e;
}

.node-title {
  color: var(--text);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.node-title.has-content {
  color: #374151;
}

.node-title.selected {
  color: var(--primary);
  font-weight: 500;
}

.read-check {
  color: #22c55e;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.star-badge {
  color: #f59e0b;
  font-size: 14px;
  flex-shrink: 0;
  animation: star-pulse 2s ease-in-out infinite;
}

@keyframes star-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.node-children {
  margin-left: 4px;
}
</style>
