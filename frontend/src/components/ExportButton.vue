<script setup>
import { ref } from 'vue'
import { useTranscriptStore } from '../stores/transcript'

const props = defineProps({
  transcriptId: {
    type: [Number, String],
    required: true
  }
})

const transcriptStore = useTranscriptStore()
const showMenu = ref(false)
const exporting = ref(false)

const exportFormats = [
  {
    value: 'pdf',
    label: 'PDF 文件',
    icon: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z'
  },
  {
    value: 'docx',
    label: 'Word 文件',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
  },
  {
    value: 'md',
    label: 'Markdown',
    icon: 'M4 6h16M4 12h16m-7 6h7'
  }
]

async function handleExport(format) {
  exporting.value = true
  showMenu.value = false

  try {
    await transcriptStore.exportTranscript(props.transcriptId, format)
  } finally {
    exporting.value = false
  }
}

function toggleMenu() {
  showMenu.value = !showMenu.value
}

// 點擊外部關閉選單
function handleClickOutside(e) {
  if (!e.target.closest('.export-button-container')) {
    showMenu.value = false
  }
}

// 監聽點擊事件
if (typeof window !== 'undefined') {
  document.addEventListener('click', handleClickOutside)
}
</script>

<template>
  <div class="relative export-button-container">
    <button
      @click.stop="toggleMenu"
      :disabled="exporting"
      class="btn-primary flex items-center gap-2"
    >
      <svg v-if="exporting" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      <span>{{ exporting ? '匯出中...' : '匯出' }}</span>
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- 下拉選單 -->
    <div
      v-show="showMenu"
      class="absolute left-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-10"
    >
      <button
        v-for="format in exportFormats"
        :key="format.value"
        @click="handleExport(format.value)"
        class="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-50 flex items-center gap-3"
      >
        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="format.icon" />
        </svg>
        <span>{{ format.label }}</span>
      </button>
    </div>
  </div>
</template>
