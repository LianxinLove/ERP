import type { Metadata } from 'next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import './globals.css';
import { ReactQueryProvider } from '@/lib/react-query/ReactQueryProvider';
import { ThemeProvider } from '@/components/theme/ThemeProvider';
import { ToastProvider } from '@/components/toast/ToastProvider';
import { AuthProvider } from '@/store/auth/AuthContext';
import { ErrorBoundary } from '@/components/error-boundary/ErrorBoundary';

/**
 * Plus Jakarta Sans - 现代、专业的无衬线字体
 * @description 专为SaaS产品和仪表板设计的字体，具有友好、现代、专业的特点
 *
 * @see https://fonts.google.com/specimen/Plus+Jakarta+Sans
 * @weight 300, 400, 500, 600, 700
 */
const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-plus-jakarta-sans',
  display: 'swap',
});

/**
 * ERP系统根布局组件
 *
 * @description 应用程序的根布局，包含全局样式和状态管理
 *
 * @features
 * - React Query数据获取和缓存
 * - 认证状态管理
 * - 主题切换支持（平滑过渡）
 * - Toast通知系统
 * - 错误边界保护
 * - Plus Jakarta Sans 字体
 */
export const metadata: Metadata = {
  title: 'ERP系统',
  description: '一个功能完善的企业资源计划系统，支持采购、销售、库存、财务管理',
  keywords: ['ERP', '企业管理', 'Next.js', 'FastAPI', '采购管理', '销售管理', '库存管理', '财务管理'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning className={plusJakartaSans.variable}>
      <body className="font-sans antialiased">
        {/* 全局错误边界 */}
        <ErrorBoundary>
          {/* Toast通知系统 - 放在错误边界内以捕获错误 */}
          <ToastProvider />
          {/* 可访问性：Skip 链接允许键盘用户跳过导航直达主内容 */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr focus:fixed focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus:shadow-md transition-all"
          >
            跳转到主内容
          </a>

          {/* 主内容区域 */}
          <div id="main-content">
            <ThemeProvider>
              <ReactQueryProvider>
                <AuthProvider>{children}</AuthProvider>
              </ReactQueryProvider>
            </ThemeProvider>
          </div>
        </ErrorBoundary>
      </body>
    </html>
  );
}
