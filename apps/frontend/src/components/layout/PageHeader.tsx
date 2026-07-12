/**
 * PageHeader 页面头部组件
 * @description 统一的页面头部样式和面包屑导航
 */

"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { ChevronRight } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  breadcrumbs,
  actions,
  className,
}: PageHeaderProps) {
  const pathname = usePathname();

  // 如果没有提供面包屑，根据路径自动生成
  const generatedBreadcrumbs = React.useMemo(() => {
    if (breadcrumbs) return breadcrumbs;

    const segments = pathname.split('/').filter(Boolean);
    const items: BreadcrumbItem[] = [
      { label: '首页', href: '/' },
    ];

    let accumulatedPath = '';
    segments.forEach((segment, index) => {
      accumulatedPath += `/${segment}`;
      const isLast = index === segments.length - 1;

      items.push({
        label: formatSegment(segment),
        href: isLast ? undefined : accumulatedPath,
      });
    });

    return items;
  }, [pathname, breadcrumbs]);

  return (
    <div className={cn('space-y-4', className)}>
      {/* 面包屑 */}
      {generatedBreadcrumbs.length > 1 && (
        <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
          {generatedBreadcrumbs.map((item, index) => (
            <React.Fragment key={index}>
              {index > 0 && (
                <ChevronRight className="h-4 w-4" />
              )}
              {item.href ? (
                <Link
                  href={item.href}
                  className="hover:text-foreground transition-colors"
                >
                  {item.label}
                </Link>
              ) : (
                <span className="text-foreground font-medium">{item.label}</span>
              )}
            </React.Fragment>
          ))}
        </nav>
      )}

      {/* 标题和操作区 */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
          {description && (
            <p className="text-muted-foreground mt-1">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}

/**
 * 格式化路径段为可读文本
 */
function formatSegment(segment: string): string {
  // 移除动态路由参数（如 [id]）
  if (segment.startsWith('[') && segment.endsWith(']')) {
    return '详情';
  }

  // 转换 kebab-case 为可读文本
  return segment
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * 页面容器组件
 * @description 包含页面头部和内容区域的容器
 */
interface PageContentProps {
  header: {
    title: string;
    description?: string;
    breadcrumbs?: BreadcrumbItem[];
    actions?: React.ReactNode;
  };
  children: React.ReactNode;
  className?: string;
}

export function PageContent({ header, children, className }: PageContentProps) {
  return (
    <div className={className}>
      <PageHeader {...header} />
      <div className="mt-6">{children}</div>
    </div>
  );
}
