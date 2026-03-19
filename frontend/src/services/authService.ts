/**
 * 认证服务
 */
import api, { initTokens } from './api';
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  TokenResponse,
} from '@/types/user';

/** 用户登录 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await api.post<TokenResponse>('/auth/login', data);
  const { access_token, refresh_token } = response.data;

  // 初始化 Token
  initTokens(access_token, refresh_token);

  // 获取用户信息
  const userResponse = await api.get<User>('/auth/me');

  return {
    user: userResponse.data,
    access_token,
    refresh_token,
  };
}

/** 用户注册 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await api.post<TokenResponse>('/auth/register', data);
  const { access_token, refresh_token } = response.data;

  // 初始化 Token
  initTokens(access_token, refresh_token);

  // 获取用户信息
  const userResponse = await api.get<User>('/auth/me');

  return {
    user: userResponse.data,
    access_token,
    refresh_token,
  };
}

/** 获取当前用户信息 */
export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>('/auth/me');
  return response.data;
}

/** 刷新 Token */
export async function refreshToken(): Promise<void> {
  const response = await api.post<TokenResponse>('/auth/refresh');
  const { access_token, refresh_token } = response.data;
  initTokens(access_token, refresh_token);
}

/** 用户登出 */
export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout');
  } finally {
    // 清除本地 Token
    (window as any).__ACCESS_TOKEN__ = null;
    document.cookie = 'refresh_token=; path=/; max-age=0';
  }
}
