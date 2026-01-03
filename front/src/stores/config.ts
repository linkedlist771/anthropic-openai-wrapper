import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Config } from '@/types'
import { configApi } from '@/api'

export const useConfigStore = defineStore('config', () => {
  const configs = ref<Config[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchConfigs(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await configApi.getAll()
      configs.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取配置失败'
    } finally {
      loading.value = false
    }
  }

  async function updateConfig(key: string, value: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await configApi.update(key, { value })
      // Update local state
      const index = configs.value.findIndex(c => c.key === key)
      if (index !== -1) {
        configs.value[index].value = value
        configs.value[index].updated_at = new Date().toISOString()
      }
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新配置失败'
      return false
    } finally {
      loading.value = false
    }
  }

  async function refreshConfigs(): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await configApi.refresh()
      // Also fetch latest configs from DB
      await fetchConfigs()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '刷新配置缓存失败'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    configs,
    loading,
    error,
    fetchConfigs,
    updateConfig,
    refreshConfigs,
  }
})

