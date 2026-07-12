/**
 * API 客户端配置
 *
 * @description 基于 Axios 的 HTTP 客户端，提供统一的请求/响应处理
 *
 * @features
 * - 自动添加认证Token
 * - 统一错误处理
 * - 自动Token刷新
 * - 请求/响应拦截
 * - Cookie同步
 */

import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { toast } from 'sonner';
import Cookies from 'js-cookie';

/**
 * API基础URL
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * Token刷新状态
 */
let isRefreshing = false;
let logoutHandler: (() => void) | null = null;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

/**
 * 刷新Token超时时间（毫秒）
 * 可通过环境变量 NEXT_PUBLIC_REFRESH_TIMEOUT 配置，默认 15000ms（15秒）
 * 对于高延迟网络环境，建议增加此值
 */
const REFRESH_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_REFRESH_TIMEOUT || '15000', 10);

/**
 * 设置Token到 localStorage 和 Cookie
 */
function setTokens(accessToken: string, refreshToken: string) {
  if (typeof window === 'undefined') return;

  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);

  const expires = 7;
  Cookies.set('access_token', accessToken, { expires, sameSite: 'lax' });
  Cookies.set('refresh_token', refreshToken, { expires, sameSite: 'lax' });
}

/**
 * 清除Token
 */
function clearTokens() {
  if (typeof window === 'undefined') return;

  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');

  Cookies.remove('access_token');
  Cookies.remove('refresh_token');
}

/**
 * 设置登出处理函数
 *
 * @param logout - 登出函数
 */
export function setLogoutHandler(logout: () => void) {
  logoutHandler = logout;
}

/**
 * 更新登出处理函数（支持动态更新）
 *
 * @param logout - 新的登出函数
 */
export function updateLogoutHandler(logout: () => void) {
  logoutHandler = logout;
}

/**
 * 处理队列中的请求
 *
 * @description 处理所有等待 token 刷新的请求
 * - 如果有错误，所有请求都被拒绝
 * - 如果成功，所有请求都获得新 token 并重试
 */
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      // 解析 promise 并传递新 token
      // 调用方负责使用这个 token 重试请求
      prom.resolve(token);
    }
  });
  // 清空队列
  failedQueue = [];
};

/**
 * 创建 API 客户端实例
 *
 * @returns 配置好的 Axios 实例
 */
export function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  /**
   * 请求拦截器
   * - 自动添加 Access Token
   */
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // 从 localStorage 获取 Token (仅在客户端环境)
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');

        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }

      return config;
    },
    error => {
      return Promise.reject(error);
    }
  );

  /**
   * 响应拦截器
   * - 处理 Token 过期
   * - 统一错误提示
   */
  client.interceptors.response.use(
    response => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

      // 401 错误 - Token 过期
      if (error.response?.status === 401 && !originalRequest._retry) {
        // 如果正在刷新，将请求加入队列
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then(token => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              return client(originalRequest);
            })
            .catch(err => {
              return Promise.reject(err);
            });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
          // 尝试刷新 Token
          const refreshToken = localStorage.getItem('refresh_token');

          if (!refreshToken) {
            throw new Error('No refresh token');
          }

          // 添加超时保护
          const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('Token refresh timeout')), REFRESH_TIMEOUT);
          });

          const response = await Promise.race([
            axios.post(`${API_BASE_URL}/api/auth/refresh`, {
              refresh_token: refreshToken,
            }),
            timeoutPromise,
          ]) as any;

          const { access_token, refresh_token: newRefreshToken } = response.data;

          // 更新 Token
          setTokens(access_token, newRefreshToken || refreshToken);

          // 处理队列中的请求
          processQueue(null, access_token);

          // 重试原请求
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }

          return client(originalRequest);
        } catch (refreshError) {
          // 刷新失败，清除Token并登出
          processQueue(refreshError, null);
          clearTokens();

          // 调用登出处理函数
          if (logoutHandler) {
            logoutHandler();
          }

          toast.error('登录已过期，请重新登录');
          return Promise.reject(refreshError);
        } finally {
          isRefreshing = false;
        }
      }

      // 其他错误处理
      if (error.response) {
        const status = error.response.status;
        const message = (error.response.data as any)?.message || '请求失败';

        switch (status) {
          case 400:
            toast.error(message);
            break;
          case 403:
            toast.error('没有权限执行此操作');
            break;
          case 404:
            toast.error('请求的资源不存在');
            break;
          case 500:
            toast.error('服务器错误，请稍后重试');
            break;
          default:
            toast.error(message);
        }
      } else if (error.request) {
        toast.error('网络错误，请检查您的网络连接');
      }

      return Promise.reject(error);
    }
  );

  return client;
}

/**
 * 默认 API 客户端实例
 */
export const apiClient = createApiClient();
