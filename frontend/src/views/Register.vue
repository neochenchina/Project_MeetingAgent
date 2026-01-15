<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const localError = ref('')

async function handleSubmit() {
  localError.value = ''

  if (password.value !== confirmPassword.value) {
    localError.value = '兩次輸入的密碼不一致'
    return
  }

  if (password.value.length < 6) {
    localError.value = '密碼長度至少需要 6 個字元'
    return
  }

  const success = await authStore.register(email.value, password.value)
  if (success) {
    router.push('/')
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="flex justify-center mb-4">
          <svg class="w-16 h-16 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </div>
        <h1 class="text-3xl font-bold text-gray-900">語音摘要助手</h1>
        <p class="text-gray-500 mt-2">建立新帳號</p>
      </div>

      <!-- 註冊表單 -->
      <div class="card">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- 錯誤訊息 -->
          <div v-if="localError || authStore.error" class="bg-red-50 text-red-600 px-4 py-3 rounded-lg text-sm">
            {{ localError || authStore.error }}
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              電子郵件
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="input-field"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密碼
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="input-field"
              placeholder="至少 6 個字元"
            />
          </div>

          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
              確認密碼
            </label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              required
              class="input-field"
              placeholder="再次輸入密碼"
            />
          </div>

          <button
            type="submit"
            :disabled="authStore.loading"
            class="btn-primary w-full flex items-center justify-center"
          >
            <svg v-if="authStore.loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ authStore.loading ? '註冊中...' : '註冊' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-gray-500 text-sm">
            已經有帳號？
            <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
              立即登入
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
