'use client';

/**
 * 认证上下文
 *
 * @description 提供全局认证状态和操作
 *
 * @features
 * - 登录/注册/登出
 * - 自动Token刷新
 * - 用户信息缓存
 * - 持久化存储
 */

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import Cookies from 'js-cookie';

import type { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types/auth';
import { authApi } from '@/api/auth';
import { PermissionProvider } from '@/store/permission/PermissionContext';

/**
 * 认证上下文类型
 */
interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * 认证提供者属性
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * 从 localStorage 获取 token
 */
function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * 设置 Token 到 localStorage 和 Cookie
 */
function setTokens(accessToken: string, refreshToken: string) {
  if (typeof window === 'undefined') return;

  // 保存到 localStorage
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);

  // 保存到 Cookie（供 middleware 使用）
  // 7天有效期
  const expires = 7;
  Cookies.set('access_token', accessToken, { expires, sameSite: 'lax' });
  Cookies.set('refresh_token', refreshToken, { expires, sameSite: 'lax' });
}

/**
 * 清除 Token
 */
function clearTokens() {
  if (typeof window === 'undefined') return;

  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');

  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
}

/**
 * 检查 token 是否有效（未过期）
 */
function isTokenValid(token: string): boolean {
  if (!token || token.length === 0) {
    return false;
  }

  try {
    // JWT token 格式: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }

    // 解码 payload
    const payload = JSON.parse(atob(parts[1]));

    // 检查过期时间
    if (!payload.exp) {
      return false; // 没有 exp 字段的 token 被认为是无效的
    }

    // 检查是否已过期
    // 使用 30 秒的缓冲时间来处理客户端-服务器时钟偏差
    // 这确保即使客户端时钟略微领先于服务器时钟，令牌仍然被视为有效
    const now = Math.floor(Date.now() / 1000);
    // 正确的逻辑：当前时间 >= 过期时间 - 缓冲时间 时，token 已过期
    const expired = now >= (payload.exp - 30);

    return !expired;
  } catch {
    return false;
  }
}

/**
 * 检查是否有有效的 token
 */
function hasValidToken(): boolean {
  const token = getAccessToken();
  return !!token && isTokenValid(token);
}

/**
 * 认证提供者组件
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const queryClient = useQueryClient();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 检查 localStorage 中的 token，初始化认证状态
  // 使用 useLayoutEffect 确保在渲染前执行，避免闪烁
  useEffect(() => {
    // 只在客户端执行
    if (typeof window === 'undefined') return;

    const hasToken = hasValidToken();
    setIsAuthenticated(hasToken);
    setIsInitialized(true);
  }, []);

  // 获取当前用户信息 - 只在有 token 时才执行
  const {
    data: user,
    isLoading,
    refetch: refreshUser,
    error: authError,
  } = useQuery({
    queryKey: ['auth', 'user'],
    queryFn: () => authApi.getCurrentUser(),
    // 只在有 token 时才执行查询
    enabled: isAuthenticated,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5分钟
  });

  // 根据用户数据和错误更新认证状态
  // 注意：不在这里进行重定向，由 AuthenticatedLayout 统一处理
  useEffect(() => {
    if (!isInitialized) return;

    if (user) {
      setIsAuthenticated(true);
      setError(null);
    } else if (authError) {
      // API 调用失败，说明 token 无效
      setIsAuthenticated(false);
      // 清除无效的 token
      clearTokens();
      setError(authError.message || '认证失败');
    } else if (!isLoading && !hasValidToken()) {
      // 没有 token 且不在加载中
      setIsAuthenticated(false);
    }
  }, [user, authError, isLoading, isInitialized]);

  // 登录
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data: AuthResponse) => {
      // 保存Token
      setTokens(data.access_token, data.refresh_token);

      // 立即更新用户信息到缓存
      queryClient.setQueryData(['auth', 'user'], data.user);
      setIsAuthenticated(true);
      setError(null);

      toast.success('登录成功');
    },
    onError: (error: Error) => {
      setError(error.message || '登录失败');
      toast.error(error.message || '登录失败');
    },
  });

  // 注册
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (data: AuthResponse) => {
      // 保存Token
      setTokens(data.access_token, data.refresh_token);

      // 立即更新用户信息到缓存
      queryClient.setQueryData(['auth', 'user'], data.user);
      setIsAuthenticated(true);
      setError(null);

      toast.success('注册成功');
    },
    onError: (error: Error) => {
      setError(error.message || '注册失败');
      toast.error(error.message || '注册失败');
    },
  });

  // 登出
  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      // 清除Token
      clearTokens();

      // 清除用户信息
      queryClient.setQueryData(['auth', 'user'], null);
      queryClient.removeQueries({ queryKey: ['auth', 'user'] });
      setIsAuthenticated(false);

      // 清除所有缓存
      queryClient.clear();

      toast.success('已退出登录');
    },
  });

  /**
   * 登录
   */
  const login = useCallback(
    async (credentials: LoginRequest) => {
      await loginMutation.mutateAsync(credentials);
    },
    [loginMutation]
  );

  /**
   * 注册
   */
  const register = useCallback(
    async (data: RegisterRequest) => {
      await registerMutation.mutateAsync(data);
    },
    [registerMutation]
  );

  /**
   * 登出
   */
  const logout = useCallback(async () => {
    try {
      await logoutMutation.mutateAsync();
    } catch (error) {
      // 即使API调用失败，也清除本地状态
      clearTokens();
      queryClient.setQueryData(['auth', 'user'], null);
      queryClient.removeQueries({ queryKey: ['auth', 'user'] });
      setIsAuthenticated(false);
      queryClient.clear();
    }
  }, [logoutMutation, queryClient]);

  /**
   * 刷新用户信息
   */
  const handleRefreshUser = useCallback(async () => {
    await refreshUser();
  }, [refreshUser]);

  const value: AuthContextValue = {
    user: user || null,
    isAuthenticated,
    isLoading: isLoading || !isInitialized,
    isInitialized,
    error,
    login,
    register,
    logout,
    refreshUser: handleRefreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      <PermissionProvider user={user || null}>{children}</PermissionProvider>
    </AuthContext.Provider>
  );
}

/**
 * 使用认证上下文
 *
 * @throws {Error} 如果不在AuthProvider内使用
 * @returns 认证上下文值
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth 必须在 AuthProvider 内使用');
  }
  return context;
}
