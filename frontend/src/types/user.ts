/**
 * 用户相关类型定义
 */

/** 用户信息 */
export interface User {
  id: number;
  email: string;
  nickname: string | null;
  is_active: boolean;
  role: string;
  created_at: string;
  updated_at: string;
}

/** 注册请求 */
export interface RegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

/** 登录请求 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Token 响应 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

/** 认证响应 */
export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
}

/** 刷新 Token 请求 */
export interface RefreshTokenRequest {
  refresh_token: string;
}
