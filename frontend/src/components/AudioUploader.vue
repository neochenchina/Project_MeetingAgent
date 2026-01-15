<script setup>
import { ref } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['upload'])

const isDragging = ref(false)
const fileInput = ref(null)

const acceptedTypes = [
  'audio/mpeg',
  'audio/mp3',
  'audio/wav',
  'audio/ogg',
  'audio/m4a',
  'audio/aac',
  'audio/flac',
  'audio/webm',
  'video/mp4',
  'video/webm'
]

const acceptedExtensions = '.mp3,.wav,.ogg,.m4a,.aac,.flac,.webm,.mp4'

function handleDragEnter(e) {
  e.preventDefault()
  if (!props.disabled) {
    isDragging.value = true
  }
}

function handleDragLeave(e) {
  e.preventDefault()
  isDragging.value = false
}

function handleDragOver(e) {
  e.preventDefault()
}

function handleDrop(e) {
  e.preventDefault()
  isDragging.value = false

  if (props.disabled) return

  const files = e.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

function handleFileSelect(e) {
  const files = e.target.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

function processFile(file) {
  // 檢查檔案類型
  const isValidType = acceptedTypes.includes(file.type) ||
    file.name.match(/\.(mp3|wav|ogg|m4a|aac|flac|webm|mp4)$/i)

  if (!isValidType) {
    alert('不支援的檔案格式。請上傳 MP3、WAV、OGG、M4A、AAC、FLAC、WEBM 或 MP4 檔案。')
    return
  }

  // 檢查檔案大小（最大 500MB）
  const maxSize = 500 * 1024 * 1024
  if (file.size > maxSize) {
    alert('檔案太大。最大支援 500MB。')
    return
  }

  emit('upload', file)
}

function triggerFileSelect() {
  if (!props.disabled) {
    fileInput.value?.click()
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<template>
  <div
    :class="[
      'upload-zone',
      { 'drag-over': isDragging },
      { 'opacity-50 cursor-not-allowed': disabled }
    ]"
    @dragenter="handleDragEnter"
    @dragleave="handleDragLeave"
    @dragover="handleDragOver"
    @drop="handleDrop"
    @click="triggerFileSelect"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="acceptedExtensions"
      class="hidden"
      :disabled="disabled"
      @change="handleFileSelect"
    />

    <div class="flex flex-col items-center">
      <!-- 上傳圖示 -->
      <div class="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
      </div>

      <!-- 說明文字 -->
      <p class="text-gray-600 font-medium mb-1">
        拖曳音檔到此處，或點擊選擇檔案
      </p>
      <p class="text-gray-400 text-sm">
        支援 MP3、WAV、OGG、M4A、AAC、FLAC、WEBM、MP4
      </p>
      <p class="text-gray-400 text-xs mt-1">
        最大 500MB
      </p>
    </div>
  </div>
</template>
