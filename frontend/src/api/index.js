import axios from 'axios'

// 建立 axios 實例
const api = axios.create({
  baseURL: '/api',
  timeout: 600000, // 10 分鐘，因為音檔處理需要時間
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 回應攔截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 處理 401 未授權
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // 如果不在登入頁，導向登入頁
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
