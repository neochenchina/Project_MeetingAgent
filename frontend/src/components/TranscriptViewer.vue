<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  text: {
    type: String,
    default: ''
  },
  segments: {
    type: Array,
    default: () => []
  },
  speakers: {
    type: Object,
    default: () => ({})
  }
})

const viewMode = ref('text') // 'text' | 'segments'
const expanded = ref(false)

const hasSegments = computed(() => props.segments && props.segments.length > 0)

const displayText = computed(() => {
  if (!props.text) return ''
  if (expanded.value) return props.text
  // 顯示前 500 字
  return props.text.length > 500 ? props.text.substring(0, 500) + '...' : props.text
})

function formatTime(seconds) {
  if (!seconds && seconds !== 0) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function getSpeakerColor(speaker) {
  const colors = [
    'bg-blue-100 text-blue-700',
    'bg-green-100 text-green-700',
    'bg-purple-100 text-purple-700',
    'bg-orange-100 text-orange-700',
    'bg-pink-100 text-pink-700',
    'bg-cyan-100 text-cyan-700'
  ]
  // 根據 speaker 名稱取得固定顏色
  const index = speaker ? speaker.charCodeAt(speaker.length - 1) % colors.length : 0
  return colors[index]
}

function copyToClipboard() {
  navigator.clipboard.writeText(props.text)
    .then(() => alert('已複製到剪貼簿'))
    .catch(() => alert('複製失敗'))
}
</script>

<template>
  <div class="card">
    <!-- 標題列 -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">轉錄內容</h2>

      <div class="flex items-center gap-2">
        <!-- 檢視模式切換 -->
        <div v-if="hasSegments" class="flex bg-gray-100 rounded-lg p-1">
          <button
            @click="viewMode = 'text'"
            :class="[
              'px-3 py-1 text-sm rounded-md transition-colors',
              viewMode === 'text' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            ]"
          >
            純文字
          </button>
          <button
            @click="viewMode = 'segments'"
            :class="[
              'px-3 py-1 text-sm rounded-md transition-colors',
              viewMode === 'segments' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'
            ]"
          >
            時間軸
          </button>
        </div>

        <!-- 複製按鈕 -->
        <button
          @click="copyToClipboard"
          class="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          title="複製全文"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 純文字模式 -->
    <div v-if="viewMode === 'text'" class="prose max-w-none">
      <p class="text-gray-700 whitespace-pre-wrap leading-relaxed">{{ displayText }}</p>

      <button
        v-if="text && text.length > 500"
        @click="expanded = !expanded"
        class="text-primary-600 hover:text-primary-700 text-sm font-medium mt-2"
      >
        {{ expanded ? '收起' : '展開全文' }}
      </button>
    </div>

    <!-- 時間軸模式 -->
    <div v-else class="space-y-3 max-h-96 overflow-y-auto">
      <div
        v-for="(segment, index) in segments"
        :key="index"
        class="flex gap-3"
      >
        <!-- 時間戳 -->
        <div class="flex-shrink-0 w-20 text-right">
          <span class="text-xs text-gray-400 font-mono">
            {{ formatTime(segment.start) }}
          </span>
        </div>

        <!-- 說話者標籤 -->
        <div v-if="segment.speaker" class="flex-shrink-0">
          <span
            :class="getSpeakerColor(segment.speaker)"
            class="px-2 py-0.5 text-xs rounded-full"
          >
            {{ segment.speaker }}
          </span>
        </div>

        <!-- 內容 -->
        <p class="flex-1 text-gray-700 text-sm">{{ segment.text }}</p>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-if="!text && segments.length === 0" class="text-center py-8 text-gray-400">
      <p>尚無轉錄內容</p>
    </div>
  </div>
</template>
