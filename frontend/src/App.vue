<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userEmail = computed(() => authStore.user?.email)

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 導航列 -->
    <nav v-if="isAuthenticated" class="bg-white shadow-sm border-b border-gray-100">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo 和主選單 -->
          <div class="flex items-center space-x-8">
            <router-link to="/" class="flex items-center space-x-2">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
              <span class="font-bold text-xl text-gray-900">語音摘要助手</span>
            </router-link>

            <div class="hidden sm:flex items-center space-x-4">
              <router-link
                to="/"
                class="px-3 py-2 rounded-lg text-gray-600 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                active-class="text-primary-600 bg-primary-50"
              >
                上傳音檔
              </router-link>
              <router-link
                to="/history"
                class="px-3 py-2 rounded-lg text-gray-600 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                active-class="text-primary-600 bg-primary-50"
              >
                歷史記錄
              </router-link>
            </div>
          </div>

          <!-- 使用者選單 -->
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-500 hidden sm:block">{{ userEmail }}</span>
            <button
              @click="handleLogout"
              class="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 手機版選單 -->
      <div class="sm:hidden border-t border-gray-100">
        <div class="flex justify-around py-2">
          <router-link
            to="/"
            class="flex flex-col items-center px-3 py-2 text-gray-600"
            active-class="text-primary-600"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span class="text-xs mt-1">上傳</span>
          </router-link>
          <router-link
            to="/history"
            class="flex flex-col items-center px-3 py-2 text-gray-600"
            active-class="text-primary-600"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-xs mt-1">記錄</span>
          </router-link>
        </div>
      </div>
    </nav>

    <!-- 主要內容 -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>
  </div>
</template>
