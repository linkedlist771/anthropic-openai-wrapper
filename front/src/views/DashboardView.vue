<script setup lang="ts">
import { ref, onMounted } from 'vue'
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

async function syncAllConfigs() {
  saveLoading.value = true
  const success = await configStore.syncConfigs()
  saveLoading.value = false
  
  if (success) {
    successMessage.value = '配置已同步到环境变量'
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
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="logo">AI逆向</div>
      
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
          @click="syncAllConfigs"
          :disabled="saveLoading"
        >
          🔄 同步配置到环境
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
            <input
              v-if="editingConfig === config.key"
              v-model="editValue"
              :type="isSecretKey(config.key) ? 'password' : 'text'"
              class="form-input"
              :placeholder="`输入 ${config.key} 的值`"
            />
            <input
              v-else
              :value="config.value"
              :type="isSecretKey(config.key) ? 'password' : 'text'"
              class="form-input"
              readonly
              disabled
            />
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

