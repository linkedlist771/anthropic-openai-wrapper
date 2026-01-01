import axios from 'axios'
import type { 
  TokenResponse, 
  LoginRequest, 
  User, 
  Config, 
  ChangePasswordRequest, 
  ChangeUsernameRequest,
  ChangeUsernameResponse,
  ConfigUpdateRequest,
  MessageResponse 
} from '@/types'

const api = axios.create({
  baseURL: '/api/admin',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (data: LoginRequest) => 
    api.post<TokenResponse>('/login', data),
  
  getMe: () => 
    api.get<User>('/me'),
  
  changePassword: (data: ChangePasswordRequest) => 
    api.post<MessageResponse>('/change-password', data),
  
  changeUsername: (data: ChangeUsernameRequest) => 
    api.post<ChangeUsernameResponse>('/change-username', data),
}

export const configApi = {
  getAll: () => 
    api.get<Config[]>('/configs'),
  
  get: (key: string) => 
    api.get<Config>(`/configs/${key}`),
  
  update: (key: string, data: ConfigUpdateRequest) => 
    api.put<MessageResponse>(`/configs/${key}`, data),
  
  sync: () => 
    api.post<MessageResponse>('/configs/sync'),
}

export default api

