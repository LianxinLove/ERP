/**
 * StatCard 统计卡片组件
 * @description 用于展示统计数据的卡片组件
 */

"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  description?: string;
  className?: string;
  onClick?: () => void;
}

export function StatCard({
  title,
  value,
  icon,
  trend,
  description,
  className,
  onClick,
}: StatCardProps) {
  const trendIcon = trend?.direction === 'up' ? (
    <TrendingUp className="h-4 w-4 text-green-600" />
  ) : trend?.direction === 'down' ? (
    <TrendingDown className="h-4 w-4 text-red-600" />
  ) : (
    <Minus className="h-4 w-4 text-muted-foreground" />
  );

  const trendColor =
    trend?.direction === 'up'
      ? 'text-green-600'
      : trend?.direction === 'down'
      ? 'text-red-600'
      : 'text-muted-foreground';

  return (
    <Card
      className={cn(
        'transition-all hover:shadow-md',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {(trend || description) && (
          <div className="mt-1 flex items-center gap-2 text-xs">
            {trend && (
              <div className={cn('flex items-center gap-1', trendColor)}>
                {trendIcon}
                <span>{Math.abs(trend.value)}%</span>
              </div>
            )}
            {description && (
              <p className="text-muted-foreground">{description}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * 统计卡片网格组件
 */
interface StatCardGridProps {
  children: React.ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4 | 5;
}

export function StatCardGrid({ children, className, cols = 4 }: StatCardGridProps) {
  const colsClass = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5',
  }[cols];

  return (
    <div className={cn('grid gap-4', colsClass, className)}>{children}</div>
  );
}

/**
 * 快速链接卡片组件
 */
interface QuickLinkCardProps {
  title: string;
  description: string;
  href: string;
  icon?: React.ReactNode;
  className?: string;
}

export function QuickLinkCard({
  title,
  description,
  href,
  icon,
  className,
}: QuickLinkCardProps) {
  return (
    <a
      href={href}
      className={cn(
        'block transition-all hover:shadow-md',
        className
      )}
    >
      <Card className="h-full">
        <CardHeader>
          <div className="flex items-center gap-3">
            {icon && <div className="text-muted-foreground">{icon}</div>}
            <CardTitle className="text-base">{title}</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{description}</p>
          <p className="text-sm text-primary mt-2 hover:underline">
            查看详情 →
          </p>
        </CardContent>
      </Card>
    </a>
  );
}
