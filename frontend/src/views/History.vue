<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTranscriptStore } from '../stores/transcript'

const router = useRouter()
const transcriptStore = useTranscriptStore()

const page = ref(1)
const totalPages = ref(1)

onMounted(async () => {
  await loadTranscripts()
})

async function loadTranscripts() {
  const result = await transcriptStore.fetchTranscripts(page.value)
  if (result) {
    totalPages.value = Math.ceil(result.total / 20)
  }
}

function viewDetail(id) {
  router.push(`/transcript/${id}`)
}

async function handleDelete(id) {
  if (confirm('確定要刪除這筆記錄嗎？')) {
    await transcriptStore.deleteTranscript(id)
  }
}

function formatDate(dateString) {
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

function getStatusBadge(status) {
  const badges = {
    completed: { class: 'bg-green-100 text-green-700', text: '已完成' },
    processing: { class: 'bg-yellow-100 text-yellow-700', text: '處理中' },
    failed: { class: 'bg-red-100 text-red-700', text: '失敗' }
  }
  return badges[status] || badges.completed
}

async function changePage(newPage) {
  page.value = newPage
  await loadTranscripts()
}
</script>

<template>
  <div class="space-y-6">
    <!-- 頁面標題 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">歷史記錄</h1>
        <p class="text-gray-500 mt-1">查看過往的轉錄記錄</p>
      </div>
      <router-link to="/" class="btn-primary">
        上傳新檔案
      </router-link>
    </div>

    <!-- 載入中 -->
    <div v-if="transcriptStore.loading" class="card">
      <div class="flex justify-center py-12">
        <div class="loading-spinner w-8 h-8"></div>
      </div>
    </div>

    <!-- 空狀態 -->
    <div v-else-if="transcriptStore.transcripts.length === 0" class="card text-center py-12">
      <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-500">尚無轉錄記錄</p>
      <router-link to="/" class="btn-primary inline-block mt-4">
        上傳第一個音檔
      </router-link>
    </div>

    <!-- 記錄列表 -->
    <div v-else class="space-y-4">
      <div
        v-for="transcript in transcriptStore.transcripts"
        :key="transcript.id"
        class="card hover:shadow-md transition-shadow cursor-pointer"
        @click="viewDetail(transcript.id)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <!-- 標題和狀態 -->
            <div class="flex items-center gap-2 mb-2">
              <h3 class="font-semibold text-gray-900 truncate">
                {{ transcript.title || transcript.original_filename }}
              </h3>
              <span
                :class="getStatusBadge(transcript.status).class"
                class="px-2 py-0.5 text-xs rounded-full flex-shrink-0"
              >
                {{ getStatusBadge(transcript.status).text }}
              </span>
            </div>

            <!-- 摘要預覽 -->
            <p v-if="transcript.summary" class="text-gray-600 text-sm line-clamp-2 mb-3">
              {{ transcript.summary.substring(0, 150) }}...
            </p>

            <!-- 元資料 -->
            <div class="flex flex-wrap items-center gap-4 text-sm text-gray-400">
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ formatDuration(transcript.audio_duration) }}
              </span>
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(transcript.created_at) }}
              </span>
              <span v-if="transcript.language" class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
                {{ transcript.language.toUpperCase() }}
              </span>
            </div>
          </div>

          <!-- 刪除按鈕 -->
          <button
            @click.stop="handleDelete(transcript.id)"
            class="p-2 text-gray-400 hover:text-red-500 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="flex justify-center gap-2 pt-4">
        <button
          v-for="p in totalPages"
          :key="p"
          @click="changePage(p)"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            p === page
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          ]"
        >
          {{ p }}
        </button>
      </div>
    </div>
  </div>
</template>
