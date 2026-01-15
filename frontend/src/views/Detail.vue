<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTranscriptStore } from '../stores/transcript'
import TranscriptViewer from '../components/TranscriptViewer.vue'
import SummaryCard from '../components/SummaryCard.vue'
import ExportButton from '../components/ExportButton.vue'

const route = useRoute()
const router = useRouter()
const transcriptStore = useTranscriptStore()

const showRegenerateModal = ref(false)
const newSummaryStyle = ref('meeting')

const transcript = computed(() => transcriptStore.currentTranscript)

onMounted(async () => {
  await transcriptStore.fetchTranscript(route.params.id)
})

async function handleRegenerate() {
  await transcriptStore.regenerateSummary(route.params.id, newSummaryStyle.value)
  showRegenerateModal.value = false
}

async function handleDelete() {
  if (confirm('確定要刪除這筆記錄嗎？')) {
    const success = await transcriptStore.deleteTranscript(route.params.id)
    if (success) {
      router.push('/history')
    }
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(seconds) {
  if (!seconds) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function getSummaryStyleLabel(style) {
  const labels = {
    meeting: '會議紀錄',
    article: '文章摘要',
    brief: '簡短重點'
  }
  return labels[style] || style
}
</script>

<template>
  <div class="space-y-6">
    <!-- 載入中 -->
    <div v-if="transcriptStore.loading && !transcript" class="card">
      <div class="flex justify-center py-12">
        <div class="loading-spinner w-8 h-8"></div>
      </div>
    </div>

    <!-- 錯誤 -->
    <div v-else-if="transcriptStore.error" class="card text-center py-12">
      <svg class="w-16 h-16 mx-auto text-red-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <p class="text-red-500">{{ transcriptStore.error }}</p>
      <router-link to="/history" class="btn-secondary inline-block mt-4">
        返回列表
      </router-link>
    </div>

    <!-- 詳情內容 -->
    <template v-else-if="transcript">
      <!-- 返回按鈕和標題 -->
      <div class="flex items-center gap-4">
        <button @click="router.back()" class="p-2 text-gray-500 hover:text-gray-700">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <div class="flex-1 min-w-0">
          <h1 class="text-2xl font-bold text-gray-900 truncate">
            {{ transcript.title || transcript.original_filename }}
          </h1>
        </div>
      </div>

      <!-- 元資料卡片 -->
      <div class="card">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p class="text-gray-400">建立時間</p>
            <p class="font-medium text-gray-900">{{ formatDate(transcript.created_at) }}</p>
          </div>
          <div>
            <p class="text-gray-400">音檔長度</p>
            <p class="font-medium text-gray-900">{{ formatDuration(transcript.audio_duration) }}</p>
          </div>
          <div>
            <p class="text-gray-400">語言</p>
            <p class="font-medium text-gray-900">{{ transcript.language?.toUpperCase() || '自動' }}</p>
          </div>
          <div>
            <p class="text-gray-400">摘要風格</p>
            <p class="font-medium text-gray-900">{{ getSummaryStyleLabel(transcript.summary_style) }}</p>
          </div>
        </div>
      </div>

      <!-- 摘要 -->
      <SummaryCard
        :summary="transcript.summary"
        :style="transcript.summary_style"
        @regenerate="showRegenerateModal = true"
      />

      <!-- 轉錄內容 -->
      <TranscriptViewer
        :text="transcript.transcript_text"
        :segments="transcript.transcript_segments"
        :speakers="transcript.speakers"
      />

      <!-- 操作按鈕 -->
      <div class="flex flex-wrap gap-3">
        <ExportButton :transcript-id="transcript.id" />
        <button @click="showRegenerateModal = true" class="btn-secondary">
          重新生成摘要
        </button>
        <button @click="handleDelete" class="btn-secondary text-red-600 hover:bg-red-50">
          刪除記錄
        </button>
      </div>
    </template>

    <!-- 重新生成摘要 Modal -->
    <div
      v-if="showRegenerateModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showRegenerateModal = false"
    >
      <div class="bg-white rounded-xl max-w-md w-full p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">重新生成摘要</h3>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            選擇摘要風格
          </label>
          <select v-model="newSummaryStyle" class="input-field">
            <option value="meeting">會議紀錄</option>
            <option value="article">文章摘要</option>
            <option value="brief">簡短重點</option>
          </select>
        </div>

        <div class="flex gap-3">
          <button
            @click="showRegenerateModal = false"
            class="btn-secondary flex-1"
          >
            取消
          </button>
          <button
            @click="handleRegenerate"
            :disabled="transcriptStore.loading"
            class="btn-primary flex-1"
          >
            {{ transcriptStore.loading ? '處理中...' : '確認' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
