'use client';

/**
 * React Query Provider
 *
 * @description 提供 React Query 的全局配置和状态管理
 *
 * @features
 * - 自动缓存和重试
 * - 统一错误处理
 * - 自动Token刷新
 * - 请求/响应拦截器
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, useEffect, useLayoutEffect, type ReactNode } from 'react';
import { toast } from 'sonner';
import { setLogoutHandler } from '@/lib/api/client';

/**
 * 创建 React Query 客户端
 *
 * @returns 配置好的 QueryClient 实例
 */
export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // 5分钟缓存
        staleTime: 5 * 60 * 1000,
        // 2次重试
        retry: 2,
        // 失败时不在窗口聚焦时重试
        refetchOnWindowFocus: false,
      },
      mutations: {
        // 变更错误处理
        onError: error => {
          console.error('Mutation error:', error);

          if (error instanceof Error) {
            toast.error(error.message || '操作失败，请稍后重试');
          }
        },
      },
    },
  });
}

/**
 * React Query Provider 组件属性
 */
interface ReactQueryProviderProps {
  children: ReactNode;
  logout?: () => void;
}

/**
 * React Query Provider 组件
 *
 * @param props - 组件属性
 * @returns 包装了 React Query 的组件树
 */
export function ReactQueryProvider({ children, logout }: ReactQueryProviderProps) {
  // 使用 useState 避免客户端导航时重新创建
  const [queryClient] = useState(() => createQueryClient());

  // 使用 useLayoutEffect 在浏览器绘制前设置 logout handler
  useLayoutEffect(() => {
    if (logout) {
      setLogoutHandler(logout);
    }
  }, [logout]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* 开发环境下显示 DevTools */}
      {/* {process.env.NODE_ENV === 'development' && <ReactQueryDevtools initialIsOpen={false} />} */}
    </QueryClientProvider>
  );
}
