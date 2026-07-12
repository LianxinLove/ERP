/**
 * 认证API
 *
 * @description 用户认证相关的API调用
 */

import { apiClient } from '@/lib/api/client';
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types/auth';

/**
 * 认证API类
 */
class AuthAPI {
  /**
   * 用户登录
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);
    return response.data;
  }

  /**
   * 用户注册
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
    return response.data;
  }

  /**
   * 刷新Token
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  /**
   * 登出
   */
  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout');
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  }

  /**
   * 忘记密码
   */
  async forgotPassword(email: string): Promise<void> {
    await apiClient.post('/api/auth/forgot-password', { email });
  }

  /**
   * 重置密码
   */
  async resetPassword(token: string, newPassword: string): Promise<void> {
    await apiClient.post('/api/auth/reset-password', { token, new_password: newPassword });
  }

  /**
   * 更新个人信息
   */
  async updateProfile(data: { full_name?: string; phone?: string; avatar_url?: string }): Promise<User> {
    const response = await apiClient.patch<User>('/api/auth/me', data);
    return response.data;
  }

  /**
   * 修改密码
   */
  async changePassword(data: { current_password: string; new_password: string }): Promise<void> {
    await apiClient.post('/api/auth/change-password', data);
  }
}

/**
 * 导出认证API实例
 */
export const authApi = new AuthAPI();
