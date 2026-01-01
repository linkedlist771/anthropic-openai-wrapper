<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    errorMessage.value = '请输入用户名和密码'
    return
  }
  
  isLoading.value = true
  errorMessage.value = ''
  
  const success = await authStore.login(username.value, password.value)
  
  if (success) {
    router.push('/admin/dashboard')
  } else {
    errorMessage.value = authStore.error || '登录失败'
  }
  
  isLoading.value = false
}

function togglePassword() {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>AI逆向</h1>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="errorMessage" class="alert alert-error">
          {{ errorMessage }}
        </div>
        
        <div class="form-group">
          <div class="input-wrapper">
            <input
              v-model="username"
              type="text"
              class="form-input"
              placeholder="请输入管理员账号"
              autocomplete="username"
            />
          </div>
        </div>
        
        <div class="form-group">
          <div class="input-wrapper">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请输入管理员密码"
              autocomplete="current-password"
            />
            <button 
              type="button" 
              class="toggle-password" 
              @click="togglePassword"
              :title="showPassword ? '隐藏密码' : '显示密码'"
            >
              <svg v-if="showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
        
        <button 
          type="submit" 
          class="btn btn-primary btn-block"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>登录</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 1rem;
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
  
  h1 {
    font-size: 2.25rem;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: -0.02em;
  }
}

.login-form {
  .form-group {
    margin-bottom: 1.25rem;
  }
  
  .form-input {
    background: #f5f5f5;
    border: none;
    padding: 1.125rem 1.25rem;
    font-size: 1rem;
    border-radius: 16px;
    
    &:focus {
      background: #f0f0f0;
      box-shadow: none;
    }
  }
  
  .btn-primary {
    margin-top: 1rem;
    padding: 1.125rem;
    border-radius: 16px;
    font-size: 1.0625rem;
  }
}

.spinner {
  width: 20px;
  height: 20px;
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

