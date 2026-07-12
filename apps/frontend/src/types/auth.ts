/**
 * 认证相关类型定义
 *
 * @description 前后端共享的认证类型
 */

/**
 * 用户信息
 */
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  last_login_at?: string;
  created_at: string;
  updated_at: string;
}

/**
 * 登录请求
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * 注册请求
 */
export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  phone?: string;
}

/**
 * 认证响应
 */
export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

/**
 * 刷新Token请求
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * 忘记密码请求
 */
export interface ForgotPasswordRequest {
  email: string;
}

/**
 * 重置密码请求
 */
export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

/**
 * 认证上下文状态
 */
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/**
 * 认证上下文操作
 */
export interface AuthActions {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}
