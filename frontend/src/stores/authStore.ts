/**
 * 认证状态管理 (Zustand)
 * 使用 httpOnly Cookie 存储 refresh_token
 */
import { create } from 'zustand';
import type { User } from '@/types/user';
import { login as loginApi, register as registerApi, logout as logoutApi } from '@/services/authService';

/* eslint-disable no-unused-vars */
interface AuthState {
  // 状态
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, nickname?: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  checkAuth: () => Promise<void>;
}
/* eslint-enable no-unused-vars */

export const useAuthStore = create<AuthState>((set) => ({
  // 初始状态
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // 登录
  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await loginApi({ email, password });
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '登录失败',
        isLoading: false,
      });
      throw error;
    }
  },

  // 注册
  register: async (email: string, password: string, nickname?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await registerApi({ email, password, nickname });
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '注册失败',
        isLoading: false,
      });
      throw error;
    }
  },

  // 登出
  logout: async () => {
    set({ isLoading: true });
    try {
      await logoutApi();
    } finally {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  // 清除错误
  clearError: () => set({ error: null }),

  // 检查认证状态
  checkAuth: async () => {
    set({ isLoading: true });
    try {
      // 检查是否有 refresh_token cookie
      const hasRefreshToken = document.cookie.match(/refresh_token=/);
      if (!hasRefreshToken) {
        set({ isAuthenticated: false, isLoading: false });
        return;
      }

      // 尝试获取当前用户（会自动刷新 token）
      const { getCurrentUser } = await import('@/services/authService');
      const user = await getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
