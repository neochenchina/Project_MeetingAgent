<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  summary: {
    type: String,
    default: ''
  },
  style: {
    type: String,
    default: 'meeting'
  }
})

const emit = defineEmits(['regenerate'])

const expanded = ref(true)

const styleLabel = computed(() => {
  const labels = {
    meeting: '會議紀錄',
    article: '文章摘要',
    brief: '簡短重點'
  }
  return labels[props.style] || '摘要'
})

const styleIcon = computed(() => {
  const icons = {
    meeting: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    article: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    brief: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4'
  }
  return icons[props.style] || icons.meeting
})

function copyToClipboard() {
  navigator.clipboard.writeText(props.summary)
    .then(() => alert('已複製到剪貼簿'))
    .catch(() => alert('複製失敗'))
}
</script>

<template>
  <div class="card bg-gradient-to-br from-primary-50 to-white border-primary-100">
    <!-- 標題列 -->
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
          <svg class="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="styleIcon" />
          </svg>
        </div>
        <div>
          <h2 class="font-semibold text-gray-900">{{ styleLabel }}</h2>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <!-- 複製 -->
        <button
          @click="copyToClipboard"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          title="複製摘要"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>

        <!-- 重新生成 -->
        <button
          @click="emit('regenerate')"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          title="重新生成"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>

        <!-- 展開/收起 -->
        <button
          @click="expanded = !expanded"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg
            :class="['w-5 h-5 transition-transform', { 'rotate-180': !expanded }]"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 摘要內容 -->
    <div v-show="expanded" class="prose max-w-none">
      <div class="text-gray-700 whitespace-pre-wrap leading-relaxed">{{ summary }}</div>
    </div>

    <!-- 空狀態 -->
    <div v-if="!summary && expanded" class="text-center py-4 text-gray-400">
      <p>尚無摘要內容</p>
    </div>
  </div>
</template>
