import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useTranscriptStore = defineStore('transcript', () => {
  // 狀態
  const transcripts = ref([])
  const currentTranscript = ref(null)
  const loading = ref(false)
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const error = ref(null)

  // 取得歷史記錄列表
  async function fetchTranscripts(page = 1, limit = 20) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/transcripts', {
        params: { skip: (page - 1) * limit, limit }
      })
      transcripts.value = response.data.items
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || '取得記錄失敗'
      return null
    } finally {
      loading.value = false
    }
  }

  // 取得單筆記錄
  async function fetchTranscript(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/transcripts/${id}`)
      currentTranscript.value = response.data
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || '取得記錄失敗'
      return null
    } finally {
      loading.value = false
    }
  }

  // 上傳音檔
  async function uploadAudio(file, options = {}) {
    uploading.value = true
    uploadProgress.value = 0
    error.value = null

    const formData = new FormData()
    formData.append('file', file)
    if (options.title) formData.append('title', options.title)
    if (options.language) formData.append('language', options.language)
    if (options.summaryStyle) formData.append('summary_style', options.summaryStyle)
    if (options.enableDiarization) formData.append('enable_diarization', 'true')

    try {
      const response = await api.post('/transcripts', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          uploadProgress.value = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
        }
      })
      currentTranscript.value = response.data
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || '上傳失敗'
      return null
    } finally {
      uploading.value = false
      uploadProgress.value = 0
    }
  }

  // 刪除記錄
  async function deleteTranscript(id) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/transcripts/${id}`)
      transcripts.value = transcripts.value.filter(t => t.id !== id)
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || '刪除失敗'
      return false
    } finally {
      loading.value = false
    }
  }

  // 重新生成摘要
  async function regenerateSummary(id, style) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/transcripts/${id}/regenerate`, null, {
        params: { summary_style: style }
      })
      currentTranscript.value = response.data
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || '重新生成失敗'
      return null
    } finally {
      loading.value = false
    }
  }

  // 匯出
  async function exportTranscript(id, format) {
    try {
      const response = await api.get(`/export/${id}/${format}`, {
        responseType: 'blob'
      })

      // 建立下載連結
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url

      // 從 Content-Disposition 取得檔名
      const contentDisposition = response.headers['content-disposition']
      let filename = `transcript.${format}`
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
        if (filenameMatch) filename = filenameMatch[1]
      }

      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      return true
    } catch (e) {
      error.value = e.response?.data?.detail || '匯出失敗'
      return false
    }
  }

  return {
    transcripts,
    currentTranscript,
    loading,
    uploading,
    uploadProgress,
    error,
    fetchTranscripts,
    fetchTranscript,
    uploadAudio,
    deleteTranscript,
    regenerateSummary,
    exportTranscript
  }
})
