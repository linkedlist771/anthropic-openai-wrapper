import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const response = await authApi.login({ username, password })
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      await fetchUser()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser(): Promise<void> {
    if (!token.value) return
    try {
      const response = await authApi.getMe()
      user.value = response.data
    } catch (err) {
      logout()
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  function setToken(newToken: string): void {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    login,
    fetchUser,
    logout,
    setToken,
  }
})

