<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

// Password change form
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// Username change form
const newUsername = ref('')
const usernamePassword = ref('')
const usernameLoading = ref(false)
const usernameError = ref('')
const usernameSuccess = ref('')

onMounted(async () => {
  await authStore.fetchUser()
  newUsername.value = authStore.user?.username || ''
})

function handleLogout() {
  authStore.logout()
  router.push('/admin/login')
}

async function changePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''
  
  if (!currentPassword.value || !newPassword.value || !confirmPassword.value) {
    passwordError.value = '请填写所有密码字段'
    return
  }
  
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = '新密码两次输入不一致'
    return
  }
  
  if (newPassword.value.length < 6) {
    passwordError.value = '新密码至少需要6个字符'
    return
  }
  
  passwordLoading.value = true
  
  try {
    await authApi.changePassword({
      current_password: currentPassword.value,
      new_password: newPassword.value,
    })
    passwordSuccess.value = '密码修改成功'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (err: any) {
    passwordError.value = err.response?.data?.detail || '密码修改失败'
  } finally {
    passwordLoading.value = false
  }
}

async function changeUsername() {
  usernameError.value = ''
  usernameSuccess.value = ''
  
  if (!newUsername.value || !usernamePassword.value) {
    usernameError.value = '请填写新用户名和当前密码'
    return
  }
  
  if (newUsername.value.length < 3) {
    usernameError.value = '用户名至少需要3个字符'
    return
  }
  
  usernameLoading.value = true
  
  try {
    const response = await authApi.changeUsername({
      new_username: newUsername.value,
      password: usernamePassword.value,
    })
    
    // Update token with new username
    authStore.setToken(response.data.access_token)
    await authStore.fetchUser()
    
    usernameSuccess.value = '用户名修改成功'
    usernamePassword.value = ''
  } catch (err: any) {
    usernameError.value = err.response?.data?.detail || '用户名修改失败'
  } finally {
    usernameLoading.value = false
  }
}

function getUserInitial(): string {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'A'
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
        <h1>账号设置</h1>
        <p class="subtitle">管理您的账号和安全设置</p>
      </div>
      
      <div class="settings-grid">
        <!-- Change Username Card -->
        <div class="card settings-card">
          <h2>修改用户名</h2>
          
          <div v-if="usernameError" class="alert alert-error">
            {{ usernameError }}
          </div>
          
          <div v-if="usernameSuccess" class="alert alert-success">
            {{ usernameSuccess }}
          </div>
          
          <form @submit.prevent="changeUsername">
            <div class="form-group">
              <label>新用户名</label>
              <input
                v-model="newUsername"
                type="text"
                class="form-input"
                placeholder="输入新用户名"
              />
            </div>
            
            <div class="form-group">
              <label>当前密码</label>
              <input
                v-model="usernamePassword"
                type="password"
                class="form-input"
                placeholder="输入当前密码以确认"
              />
            </div>
            
            <button 
              type="submit"
              class="btn btn-primary"
              :disabled="usernameLoading"
            >
              <span v-if="usernameLoading" class="spinner"></span>
              <span v-else>保存用户名</span>
            </button>
          </form>
        </div>
        
        <!-- Change Password Card -->
        <div class="card settings-card">
          <h2>修改密码</h2>
          
          <div v-if="passwordError" class="alert alert-error">
            {{ passwordError }}
          </div>
          
          <div v-if="passwordSuccess" class="alert alert-success">
            {{ passwordSuccess }}
          </div>
          
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label>当前密码</label>
              <input
                v-model="currentPassword"
                type="password"
                class="form-input"
                placeholder="输入当前密码"
              />
            </div>
            
            <div class="form-group">
              <label>新密码</label>
              <input
                v-model="newPassword"
                type="password"
                class="form-input"
                placeholder="输入新密码 (至少6个字符)"
              />
            </div>
            
            <div class="form-group">
              <label>确认新密码</label>
              <input
                v-model="confirmPassword"
                type="password"
                class="form-input"
                placeholder="再次输入新密码"
              />
            </div>
            
            <button 
              type="submit"
              class="btn btn-primary"
              :disabled="passwordLoading"
            >
              <span v-if="passwordLoading" class="spinner"></span>
              <span v-else>保存密码</span>
            </button>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.settings-card {
  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e0e0e0;
  }
  
  form {
    .form-group {
      margin-bottom: 1rem;
    }
    
    .btn {
      margin-top: 0.5rem;
    }
  }
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>


