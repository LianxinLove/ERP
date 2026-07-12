/**
 * MobileCardView 移动端卡片视图组件
 * @description 在移动端将表格数据转换为卡片布局，提供更好的用户体验
 */

"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Column<T> {
  id: string;
  header: string;
  cell: (row: T) => React.ReactNode;
  className?: string;
  badgeVariant?: 'default' | 'success' | 'warning' | 'destructive' | 'info';
  hideOnMobile?: boolean;
}

interface MobileCardViewProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  className?: string;
}

export function MobileCardView<T>({
  data,
  columns,
  onRowClick,
  emptyMessage = '暂无数据',
  className,
}: MobileCardViewProps<T>) {
  // 过滤掉在移动端隐藏的列
  const visibleColumns = columns.filter(col => !col.hideOnMobile);

  if (data.length === 0) {
    return (
      <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
        <div className="text-muted-foreground/50 mb-4">
          <svg className="w-12 h-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        </div>
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {data.map((row, rowIndex) => (
        <Card
          key={rowIndex}
          className={cn(
            'transition-all duration-200',
            onRowClick && 'hover:shadow-md cursor-pointer active:scale-[0.99]'
          )}
          onClick={() => onRowClick?.(row)}
        >
          <CardContent className="p-4">
            <div className="space-y-3">
              {visibleColumns.map((column, colIndex) => {
                // 第一列作为卡片标题（通常是主要信息）
                const isTitle = colIndex === 0;
                const cellContent = column.cell(row);

                return (
                  <div
                    key={column.id}
                    className={cn(
                      'flex justify-between items-start gap-2',
                      isTitle && 'pb-3 border-b border-border'
                    )}
                  >
                    <span className={cn(
                      'text-sm flex-shrink-0',
                      isTitle ? 'font-semibold text-foreground' : 'text-muted-foreground'
                    )}>
                      {column.header}
                    </span>
                    <div className="flex-1 text-right min-w-0">
                      {column.badgeVariant ? (
                        <Badge variant={column.badgeVariant} className={cn('ml-auto', column.className)}>
                          {cellContent}
                        </Badge>
                      ) : (
                        <span className={cn(
                          'text-sm',
                          isTitle ? 'font-medium' : 'text-foreground',
                          column.className
                        )}>
                          {cellContent as React.ReactNode}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* 点击指示器 */}
            {onRowClick && (
              <div className="flex items-center justify-end mt-3 pt-3 border-t border-border">
                <span className="text-xs text-muted-foreground mr-1">查看详情</span>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

/**
 * 紧凑型移动端卡片视图（用于列表项较多的场景）
 */
interface CompactCardViewProps<T> {
  data: T[];
  getTitle: (row: T) => string;
  getSubtitle?: (row: T) => string;
  getRightElement?: (row: T) => React.ReactNode;
  onRowClick?: (row: T) => void;
  className?: string;
}

export function CompactCardView<T>({
  data,
  getTitle,
  getSubtitle,
  getRightElement,
  onRowClick,
  className,
}: CompactCardViewProps<T>) {
  return (
    <div className={cn('space-y-2', className)}>
      {data.map((row, index) => (
        <div
          key={index}
          className={cn(
            'flex items-center gap-3 p-3 rounded-lg border border-border bg-card transition-all duration-150',
            onRowClick && 'hover:bg-accent cursor-pointer active:scale-[0.99]'
          )}
          onClick={() => onRowClick?.(row)}
        >
          <div className="flex-1 min-w-0">
            <div className="font-medium text-sm truncate">{getTitle(row)}</div>
            {getSubtitle && (
              <div className="text-xs text-muted-foreground truncate">{getSubtitle(row)}</div>
            )}
          </div>
          {getRightElement && (
            <div className="flex-shrink-0">{getRightElement(row)}</div>
          )}
        </div>
      ))}
    </div>
  );
}
