/**
 * Axios API 客户端配置
 * 使用 httpOnly Cookie 存储 refresh_token，access_token 存储在内存中
 */
import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// 创建 Axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 启用 Cookie
});

// 请求拦截器：添加 access_token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从内存中获取 access_token（而不是 localStorage）
    const token = (window as any).__ACCESS_TOKEN__;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 Token 刷新
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 如果是 401 错误且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 尝试刷新 Token
        const refreshToken = getRefreshTokenFromCookie();
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}/auth/refresh`,
            { refresh_token: refreshToken },
            { withCredentials: true }
          );

          const { access_token, refresh_token } = response.data;
          setAccessToken(access_token);
          setRefreshTokenCookie(refresh_token);

          // 重试原始请求
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除 Token 并跳转到登录
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ============ Token 管理函数 ============

/** 从 Cookie 获取 Refresh Token */
function getRefreshTokenFromCookie(): string | null {
  const match = document.cookie.match(/refresh_token=([^;]+)/);
  return match ? match[1] : null;
}

/** 设置 Refresh Token 到 Cookie */
function setRefreshTokenCookie(token: string): void {
  // httpOnly Cookie 由后端设置，这里只是辅助
  document.cookie = `refresh_token=${token}; path=/; max-age=${7 * 24 * 60 * 60}; samesite=strict`;
}

/** 将 access_token 存储到内存（不是 localStorage） */
function setAccessToken(token: string): void {
  (window as any).__ACCESS_TOKEN__ = token;
}

/** 清除所有 Token */
function clearTokens(): void {
  (window as any).__ACCESS_TOKEN__ = null;
  document.cookie = 'refresh_token=; path=/; max-age=0';
}

/** 初始化 Token（从响应中提取） */
export function initTokens(access_token: string, refresh_token: string): void {
  setAccessToken(access_token);
  setRefreshTokenCookie(refresh_token);
}

export default api;
