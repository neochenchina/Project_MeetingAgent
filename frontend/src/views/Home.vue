<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTranscriptStore } from '../stores/transcript'
import AudioUploader from '../components/AudioUploader.vue'
import TranscriptViewer from '../components/TranscriptViewer.vue'
import SummaryCard from '../components/SummaryCard.vue'
import ExportButton from '../components/ExportButton.vue'

const router = useRouter()
const transcriptStore = useTranscriptStore()

const title = ref('')
const language = ref('auto')
const summaryStyle = ref('meeting')
const enableDiarization = ref(false)

const result = computed(() => transcriptStore.currentTranscript)
const isProcessing = computed(() => transcriptStore.uploading)

async function handleUpload(file) {
  await transcriptStore.uploadAudio(file, {
    title: title.value || file.name,
    language: language.value,
    summaryStyle: summaryStyle.value,
    enableDiarization: enableDiarization.value
  })
}

function viewDetail() {
  if (result.value?.id) {
    router.push(`/transcript/${result.value.id}`)
  }
}

function resetForm() {
  transcriptStore.currentTranscript = null
  title.value = ''
}
</script>

<template>
  <div class="space-y-6">
    <!-- 頁面標題 -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">上傳音檔</h1>
      <p class="text-gray-500 mt-1">上傳音檔，自動轉錄並生成摘要</p>
    </div>

    <!-- 處理中或已完成顯示結果 -->
    <template v-if="result || isProcessing">
      <!-- 處理進度 -->
      <div v-if="isProcessing" class="card">
        <div class="flex flex-col items-center py-8">
          <div class="loading-spinner w-12 h-12 mb-4"></div>
          <p class="text-gray-600 font-medium">正在處理音檔...</p>
          <p class="text-gray-400 text-sm mt-2">
            上傳進度：{{ transcriptStore.uploadProgress }}%
          </p>
          <p class="text-gray-400 text-xs mt-1">
            處理時間取決於音檔長度，請耐心等待
          </p>
        </div>
      </div>

      <!-- 處理結果 -->
      <template v-else-if="result">
        <!-- 摘要卡片 -->
        <SummaryCard :summary="result.summary" :style="result.summary_style" />

        <!-- 轉錄內容 -->
        <TranscriptViewer
          :text="result.transcript_text"
          :segments="result.transcript_segments"
          :speakers="result.speakers"
        />

        <!-- 操作按鈕 -->
        <div class="flex flex-wrap gap-3">
          <ExportButton :transcript-id="result.id" />
          <button @click="viewDetail" class="btn-secondary">
            查看詳情
          </button>
          <button @click="resetForm" class="btn-secondary">
            上傳新檔案
          </button>
        </div>
      </template>
    </template>

    <!-- 上傳表單 -->
    <template v-else>
      <!-- 選項設定 -->
      <div class="card">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">處理選項</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- 標題 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              標題（選填）
            </label>
            <input
              v-model="title"
              type="text"
              class="input-field"
              placeholder="輸入記錄標題"
            />
          </div>

          <!-- 語言 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              語言
            </label>
            <select v-model="language" class="input-field">
              <option value="auto">自動偵測</option>
              <option value="zh">中文</option>
              <option value="en">英文</option>
              <option value="ja">日文</option>
            </select>
          </div>

          <!-- 摘要風格 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              摘要風格
            </label>
            <select v-model="summaryStyle" class="input-field">
              <option value="meeting">會議紀錄</option>
              <option value="article">文章摘要</option>
              <option value="brief">簡短重點</option>
            </select>
          </div>

          <!-- 說話者辨識 -->
          <div class="flex items-center">
            <label class="flex items-center cursor-pointer">
              <input
                v-model="enableDiarization"
                type="checkbox"
                class="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <span class="ml-2 text-sm text-gray-700">
                啟用說話者辨識（處理時間較長）
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- 上傳區域 -->
      <AudioUploader
        @upload="handleUpload"
        :disabled="isProcessing"
      />

      <!-- 錯誤訊息 -->
      <div v-if="transcriptStore.error" class="bg-red-50 text-red-600 px-4 py-3 rounded-lg">
        {{ transcriptStore.error }}
      </div>
    </template>
  </div>
</template>
