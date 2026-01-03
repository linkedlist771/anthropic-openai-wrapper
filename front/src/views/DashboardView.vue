<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'

const router = useRouter()
const authStore = useAuthStore()
const configStore = useConfigStore()

const editingConfig = ref<string | null>(null)
const editValue = ref('')
const saveLoading = ref(false)
const successMessage = ref('')
// 用于记录每个配置项的密码可见状态
const visiblePasswords = reactive<Record<string, boolean>>({})

onMounted(async () => {
  await authStore.fetchUser()
  await configStore.fetchConfigs()
})

function handleLogout() {
  authStore.logout()
  router.push('/admin/login')
}

function startEdit(key: string, value: string) {
  editingConfig.value = key
  editValue.value = value
}

function cancelEdit() {
  editingConfig.value = null
  editValue.value = ''
}

async function saveConfig(key: string) {
  saveLoading.value = true
  const success = await configStore.updateConfig(key, editValue.value)
  saveLoading.value = false
  
  if (success) {
    editingConfig.value = null
    editValue.value = ''
    successMessage.value = `配置 ${key} 已更新`
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }
}

async function refreshAllConfigs() {
  saveLoading.value = true
  const success = await configStore.refreshConfigs()
  saveLoading.value = false
  
  if (success) {
    successMessage.value = '配置缓存已刷新'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }
}

function getUserInitial(): string {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'A'
}

function isSecretKey(key: string): boolean {
  return key.includes('API_KEY') || key.includes('SECRET')
}

function togglePasswordVisibility(key: string) {
  visiblePasswords[key] = !visiblePasswords[key]
}

function getInputType(key: string): string {
  if (!isSecretKey(key)) return 'text'
  return visiblePasswords[key] ? 'text' : 'password'
}
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo">Anth2OAI</div>
      
      <ul class="nav-menu">
        <li>
          <RouterLink to="/admin/dashboard">
            <span class="icon">⚙️</span>
            <span>配置管理</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/admin/settings">
            <span class="icon">👤</span>
            <span>账号设置</span>
          </RouterLink>
        </li>
      </ul>
      
      <div class="nav-footer">
        <div class="user-info">
          <div class="avatar">{{ getUserInitial() }}</div>
          <span class="username">{{ authStore.user?.username || 'Admin' }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </aside>
    
    <main class="main-content">
      <div class="page-header">
        <h1>配置管理</h1>
        <p class="subtitle">管理API密钥和系统配置</p>
      </div>
      
      <div v-if="successMessage" class="alert alert-success">
        {{ successMessage }}
      </div>
      
      <div v-if="configStore.error" class="alert alert-error">
        {{ configStore.error }}
      </div>
      
      <div class="actions-bar">
        <button 
          class="btn btn-secondary btn-sm" 
          @click="refreshAllConfigs"
          :disabled="saveLoading"
        >
          🔄 刷新配置缓存
        </button>
      </div>
      
      <div v-if="configStore.loading" class="loading">
        <span class="spinner"></span>
        <span>加载中...</span>
      </div>
      
      <div v-else class="config-list">
        <div 
          v-for="config in configStore.configs" 
          :key="config.key" 
          class="config-item"
        >
          <div class="config-header">
            <span class="config-key">{{ config.key }}</span>
            <div class="config-actions">
              <button 
                v-if="editingConfig !== config.key"
                class="btn btn-secondary btn-sm"
                @click="startEdit(config.key, config.value)"
              >
                编辑
              </button>
              <template v-else>
                <button 
                  class="btn btn-primary btn-sm"
                  @click="saveConfig(config.key)"
                  :disabled="saveLoading"
                >
                  保存
                </button>
                <button 
                  class="btn btn-secondary btn-sm"
                  @click="cancelEdit"
                >
                  取消
                </button>
              </template>
            </div>
          </div>
          
          <p class="config-description">{{ config.description }}</p>
          
          <div class="config-value">
            <div class="input-wrapper">
              <input
                v-if="editingConfig === config.key"
                v-model="editValue"
                :type="getInputType(config.key)"
                class="form-input"
                :placeholder="`输入 ${config.key} 的值`"
              />
              <input
                v-else
                :value="config.value"
                :type="getInputType(config.key)"
                class="form-input"
                readonly
                disabled
              />
              <button 
                v-if="isSecretKey(config.key)"
                type="button" 
                class="toggle-password" 
                @click="togglePasswordVisibility(config.key)"
                :title="visiblePasswords[config.key] ? '隐藏' : '显示'"
              >
                <svg v-if="visiblePasswords[config.key]" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.actions-bar {
  margin-bottom: 1.5rem;
  display: flex;
  gap: 0.75rem;
}

.loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  justify-content: center;
  
  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid #e0e0e0;
    border-top-color: #646cff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

.config-value {
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    width: 100%;
    
    .form-input {
      width: 100%;
      padding-right: 3rem;
      font-family: 'SF Mono', Monaco, Consolas, monospace;
      font-size: 0.9rem;
    }
    
    .toggle-password {
      position: absolute;
      right: 1rem;
      background: none;
      border: none;
      cursor: pointer;
      color: #666;
      padding: 0.25rem;
      display: flex;
      align-items: center;
      justify-content: center;
      
      &:hover {
        color: #333;
      }
    }
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
