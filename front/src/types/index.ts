// API Response Types
export interface User {
  id: number
  username: string
  created_at: string
  updated_at: string
}

export interface Config {
  id: number
  key: string
  value: string
  description: string | null
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface LoginRequest {
  username: string
  password: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface ChangeUsernameRequest {
  new_username: string
  password: string
}

export interface ChangeUsernameResponse {
  message: string
  access_token: string
  token_type: string
}

export interface ConfigUpdateRequest {
  value: string
}

export interface MessageResponse {
  message: string
}

export interface ApiError {
  detail: string
}


