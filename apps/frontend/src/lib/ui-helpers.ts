/**
 * UI 工具函数库
 * @description 提供通用的 UI 样式类名和工具函数，确保整个应用的 UI 一致性
 */

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * 合并 Tailwind CSS 类名
 * @description 使用 clsx 和 tailwind-merge 智能合并类名，避免冲突
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Focus Ring 样式
 * @description 标准的 focus-visible 样式，确保键盘用户能看到焦点
 */
export const focusRing = 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background';

/**
 * 去除 outline 但保留可访问性
 * @description 自定义 outline 样式时使用，确保 focus 状态可见
 */
export const outlineNoneAccessible = 'outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2';

/**
 * 按钮基础样式
 */
export const buttonBase = 'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 cursor-pointer disabled:pointer-events-none disabled:opacity-50';

/**
 * 按钮变体样式
 */
export const buttonVariants = {
  primary: `${buttonBase} ${focusRing} bg-primary text-primary-foreground hover:bg-primary/90 hover:shadow-md active:scale-95`,
  secondary: `${buttonBase} ${focusRing} bg-secondary text-secondary-foreground hover:bg-secondary/90 hover:shadow-md active:scale-95`,
  ghost: `${buttonBase} ${focusRing} bg-transparent hover:bg-accent hover:text-accent-foreground active:scale-95`,
  outline: `${buttonBase} ${focusRing} border border-input bg-transparent hover:bg-accent hover:text-accent-foreground active:scale-95`,
  destructive: `${buttonBase} ${focusRing} bg-destructive text-destructive-foreground hover:bg-destructive/90 hover:shadow-md active:scale-95`,
  link: `${buttonBase} ${focusRing} bg-transparent text-primary underline-offset-4 hover:underline`,
};

/**
 * 按钮尺寸
 */
export const buttonSizes = {
  sm: 'h-8 px-3 text-xs',
  default: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
  icon: 'h-10 w-10',
};

/**
 * 卡片样式
 */
export const cardVariants = {
  default: 'rounded-lg border bg-card text-card-foreground shadow-sm',
  hover: 'rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer',
  clickable: 'rounded-lg border bg-card text-card-foreground shadow-sm hover:shadow-md hover:border-primary/20 transition-all duration-200 cursor-pointer active:scale-[0.99]',
  glass: 'bg-card/80 backdrop-blur-md border border-border shadow-sm',
};

/**
 * 表单输入框样式
 */
export const inputStyles = {
  base: 'h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 transition-colors duration-200',
  error: 'border-destructive focus-visible:ring-destructive',
  success: 'border-success focus-visible:ring-success',
};

/**
 * 导航项样式
 */
export const navItemStyles = {
  base: 'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 cursor-pointer',
  active: 'bg-secondary text-secondary-foreground shadow-sm',
  inactive: 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
};

/**
 * 过渡动画时间
 */
export const transitions = {
  fast: 'duration-150',
  default: 'duration-200',
  slow: 'duration-300',
} as const;

/**
 * 常用过渡组合
 */
export const transitionPresets = {
  colors: 'transition-colors duration-200 ease-out',
  transform: 'transition-transform duration-200 ease-out',
  all: 'transition-all duration-200 ease-out',
  shadow: 'transition-shadow duration-200 ease-out',
} as const;

/**
 * 徽章样式
 */
export const badgeVariants = {
  success: 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success border border-success/20',
  warning: 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning/10 text-warning border border-warning/20',
  error: 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-destructive/10 text-destructive border border-destructive/20',
  info: 'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20',
};

/**
 * 表格行样式
 */
export const tableRowStyles = {
  base: 'border-b border-border transition-colors duration-150',
  hover: 'hover:bg-muted/50',
  clickable: 'cursor-pointer hover:bg-muted/50 focus-visible:bg-muted/70',
};

/**
 * 骨架屏样式
 */
export const skeletonStyles = {
  base: 'bg-muted animate-pulse rounded',
  text: 'h-4 w-full',
  title: 'h-6 w-1/2',
  circle: 'rounded-full',
  avatar: 'h-10 w-10',
};

/**
 * 获取完整的按钮类名
 */
export function getButtonClasses(variant: keyof typeof buttonVariants = 'primary', size: keyof typeof buttonSizes = 'default', className?: string) {
  return cn(buttonVariants[variant], buttonSizes[size], className);
}

/**
 * 获取卡片类名
 */
export function getCardClasses(variant: keyof typeof cardVariants = 'default', className?: string) {
  return cn(cardVariants[variant], className);
}

/**
 * 获取徽章类名
 */
export function getBadgeClasses(type: 'success' | 'warning' | 'error' | 'info', className?: string) {
  return cn(badgeVariants[type], className);
}

/**
 * 生成 aria-label
 * @description 根据上下文生成合适的 aria-label
 */
export function getAriaLabel(type: 'close' | 'menu' | 'search' | 'filter' | 'settings' | 'logout', customText?: string): string {
  const labels = {
    close: customText || '关闭',
    menu: customText || '菜单',
    search: customText || '搜索',
    filter: customText || '筛选',
    settings: customText || '设置',
    logout: customText || '退出登录',
  };
  return labels[type];
}

/**
 * 生成唯一 ID
 * @description 为可访问性属性生成唯一 ID
 */
let idCounter = 0;
export function generateId(prefix = 'id'): string {
  return `${prefix}-${++idCounter}`;
}

/**
 * 检查是否为移动端
 * @description 在客户端组件中使用，判断是否为移动设备
 */
export function isMobile(): boolean {
  if (typeof window === 'undefined') return false;
  return window.innerWidth < 768;
}

/**
 * 检查是否为触摸设备
 */
export function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false;
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

/**
 * 格式化数字为货币
 */
export function formatCurrency(amount: number, currency = 'CNY'): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency,
  }).format(amount);
}

/**
 * 格式化日期
 */
export function formatDate(date: Date | string, format: 'short' | 'long' | 'time' = 'short'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  switch (format) {
    case 'short':
      return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      }).format(dateObj);
    case 'long':
      return new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(dateObj);
    case 'time':
      return new Intl.DateTimeFormat('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      }).format(dateObj);
  }
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}

/**
 * 获取相对时间描述
 */
export function getRelativeTime(date: Date | string): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;

  return formatDate(dateObj, 'short');
}

/**
 * 确认对话框配置
 */
interface ConfirmOptions {
  /** 标题 */
  title?: string;
  /** 消息内容 */
  message?: string;
  /** 确认按钮文字 */
  confirmText?: string;
  /** 取消按钮文字 */
  cancelText?: string;
  /** 确认按钮类型 */
  variant?: 'default' | 'destructive';
}

/**
 * 显示确认对话框
 * @description 使用浏览器原生 confirm，后续可替换为自定义对话框
 * @returns Promise<boolean> - 用户是否确认
 */
export async function confirm(options: ConfirmOptions = {}): Promise<boolean> {
  const {
    title = '确认操作',
    message = '确定要执行此操作吗？',
    confirmText = '确定',
    cancelText = '取消',
  } = options;

  // 简单实现：使用 window.confirm
  // TODO: 替换为自定义 Dialog 组件
  return window.confirm(`${title}\n\n${message}`);
}

/**
 * 显示提示对话框
 */
export async function alert(message: string, title = '提示'): Promise<void> {
  // 简单实现：使用 window.alert
  // TODO: 替换为自定义 Dialog 组件
  window.alert(`${title}\n\n${message}`);
}
