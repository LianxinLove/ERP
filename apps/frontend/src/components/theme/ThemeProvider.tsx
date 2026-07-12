'use client';

/**
 * 主题提供者组件
 *
 * @description 提供亮色/暗色主题切换功能，支持平滑过渡动画
 *
 * @features
 * - 支持系统主题自动切换
 * - 主题持久化存储
 * - 平滑的主题过渡动画（300ms ease-out）
 * - 减少动画偏好支持
 */

import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { type ThemeProviderProps } from 'next-themes/dist/types';

/**
 * 主题提供者组件
 *
 * @param props - next-themes 的属性
 * @returns 包装了主题功能的组件树
 */
export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange={false}
      {...props}
    >
      {children}
    </NextThemesProvider>
  );
}

/**
 * 主题切换按钮组件
 *
 * @description 用于切换亮色/暗色主题的按钮组件
 */
export function ThemeToggle() {
  return null; // This should be implemented in a separate component
}
