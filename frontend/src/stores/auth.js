import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  // 狀態
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)

  // 計算屬性
  const isAuthenticated = computed(() => !!token.value)

  // 設定 token
  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    }
  }

  // 註冊
  async function register(email, password) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/register', { email, password })
      setToken(response.data.access_token)
      user.value = response.data.user
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || '註冊失敗'
      return false
    } finally {
      loading.value = false
    }
  }

  // 登入
  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/auth/login', { email, password })
      setToken(response.data.access_token)
      user.value = response.data.user
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || '登入失敗'
      return false
    } finally {
      loading.value = false
    }
  }

  // 取得當前使用者
  async function fetchUser() {
    if (!token.value) return

    loading.value = true
    try {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (e) {
      // Token 無效，清除
      setToken(null)
      user.value = null
    } finally {
      loading.value = false
    }
  }

  // 登出
  function logout() {
    setToken(null)
    user.value = null
  }

  // 初始化時檢查 token
  if (token.value) {
    fetchUser()
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    fetchUser
  }
})
