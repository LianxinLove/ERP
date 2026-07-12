/**
 * 认证页面布局包装器
 * @description 为需要认证的页面提供统一的布局，包含侧边栏和顶部导航
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useAuth } from '@/store/auth/AuthContext';
import { AppLayout } from './AppLayout';

interface AuthenticatedLayoutProps {
  children: React.ReactNode;
}

export function AuthenticatedLayout({ children }: AuthenticatedLayoutProps) {
  const { isAuthenticated, isLoading, isInitialized } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // 等待初始化完成后再检查认证状态
    if (isInitialized && !isLoading && !isAuthenticated) {
      // 使用 router.replace 跳转，避免触发 middleware 的重定向循环
      router.replace('/auth/login');
    }
  }, [isAuthenticated, isLoading, isInitialized, router]);

  // 在初始化完成前或加载中显示加载状态
  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // 显示加载状态而不是null，避免空白页面
    // useEffect会处理跳转到登录页
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">正在跳转到登录页...</p>
        </div>
      </div>
    );
  }

  return <AppLayout>{children}</AppLayout>;
}
