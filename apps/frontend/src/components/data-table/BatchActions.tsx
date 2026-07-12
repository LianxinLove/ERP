/**
 * BatchActions 批量操作组件
 * @description 显示已选择项目数量和批量操作按钮
 */

"use client";

import React from 'react';
import { Button } from '@/components/ui/button';
import { Download, Trash2, X, CheckSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface BatchAction {
  label: string;
  onClick: () => void;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  icon?: React.ReactNode;
  disabled?: boolean;
}

interface BatchActionsProps {
  selectedCount: number;
  totalCount?: number;
  onClearSelection?: () => void;
  onExport?: () => void;
  onDelete?: () => void;
  onConfirm?: () => void;
  onCancel?: () => void;
  customActions?: BatchAction[];
  className?: string;
  showSelectAll?: boolean;
  isAllSelected?: boolean;
  onSelectAll?: () => void;
}

export function BatchActions({
  selectedCount,
  totalCount,
  onClearSelection,
  onExport,
  onDelete,
  onConfirm,
  onCancel,
  customActions,
  className,
  showSelectAll = false,
  isAllSelected = false,
  onSelectAll,
}: BatchActionsProps) {
  if (selectedCount === 0) return null;

  return (
    <div
      className={cn(
        'flex flex-wrap items-center gap-3 bg-muted/50 border border-border rounded-lg p-3 mb-4',
        'animate-in fade-in slide-in-from-top-2 duration-300',
        className
      )}
      role="region"
      aria-label={`已选择 ${selectedCount} 项`}
    >
      {/* 选择指示器 */}
      <div className="flex items-center gap-2">
        {showSelectAll && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onSelectAll}
            className="h-8 px-2"
            aria-label={isAllSelected ? '取消全选' : '全选'}
          >
            <CheckSquare className={cn('h-4 w-4', isAllSelected && 'text-primary')} />
          </Button>
        )}
        <div className="flex items-center gap-1.5 bg-background border border-border rounded-md px-3 py-1.5">
          <span className="text-sm">已选择</span>
          <span className="text-sm font-bold text-primary">{selectedCount}</span>
          {totalCount && (
            <span className="text-sm text-muted-foreground">
              / {totalCount}
            </span>
          )}
          <span className="text-sm text-muted-foreground">项</span>
        </div>
      </div>

      {/* 分隔线 */}
      <div className="hidden sm:block w-px h-6 bg-border" />

      {/* 默认操作按钮 */}
      <div className="flex flex-wrap items-center gap-2">
        {onClearSelection && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearSelection}
            className="h-8"
            aria-label="清除选择"
          >
            <X className="h-4 w-4 mr-1" />
            取消选择
          </Button>
        )}

        {onExport && (
          <Button
            variant="outline"
            size="sm"
            onClick={onExport}
            className="h-8"
          >
            <Download className="h-4 w-4 mr-1" />
            导出
          </Button>
        )}

        {onConfirm && (
          <Button
            variant="default"
            size="sm"
            onClick={onConfirm}
            className="h-8"
          >
            <CheckSquare className="h-4 w-4 mr-1" />
            批量确认
          </Button>
        )}

        {onCancel && (
          <Button
            variant="outline"
            size="sm"
            onClick={onCancel}
            className="h-8"
          >
            <X className="h-4 w-4 mr-1" />
            批量取消
          </Button>
        )}

        {onDelete && (
          <Button
            variant="destructive"
            size="sm"
            onClick={onDelete}
            className="h-8"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            批量删除
          </Button>
        )}
      </div>

      {/* 自定义操作按钮 */}
      {customActions && customActions.length > 0 && (
        <>
          <div className="w-px h-6 bg-border" />
          <div className="flex flex-wrap items-center gap-2">
            {customActions.map((action, index) => (
              <Button
                key={index}
                variant={action.variant || 'outline'}
                size="sm"
                onClick={action.onClick}
                disabled={action.disabled}
                className="h-8"
              >
                {action.icon}
                {action.label}
              </Button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/**
 * 紧凑型批量操作栏（用于表格上方）
 */
interface CompactBatchActionsProps {
  selectedCount: number;
  onClearSelection: () => void;
  actions?: Array<{
    label: string;
    onClick: () => void;
    variant?: 'default' | 'destructive' | 'outline';
  }>;
}

export function CompactBatchActions({
  selectedCount,
  onClearSelection,
  actions = [],
}: CompactBatchActionsProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="flex items-center justify-between bg-muted/50 border border-border rounded px-3 py-2 mb-3">
      <span className="text-sm">
        已选择 <span className="font-semibold text-primary">{selectedCount}</span> 项
      </span>
      <div className="flex items-center gap-2">
        {actions.map((action, index) => (
          <Button
            key={index}
            variant={action.variant || 'outline'}
            size="sm"
            onClick={action.onClick}
            className="h-7 text-xs"
          >
            {action.label}
          </Button>
        ))}
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearSelection}
          className="h-7 text-xs"
        >
          取消
        </Button>
      </div>
    </div>
  );
}

/**
 * 选择状态提示
 */
interface SelectionStatusProps {
  selectedCount: number;
  totalCount: number;
  onSelectAll?: () => void;
  onClear?: () => void;
}

export function SelectionStatus({
  selectedCount,
  totalCount,
  onSelectAll,
  onClear,
}: SelectionStatusProps) {
  const isAllSelected = selectedCount === totalCount && totalCount > 0;
  const isPartialSelected = selectedCount > 0 && !isAllSelected;

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Button
        variant="ghost"
        size="sm"
        onClick={isAllSelected || isPartialSelected ? onClear : onSelectAll}
        className="h-8 px-2"
        aria-label={
          isAllSelected
            ? '取消全选'
            : isPartialSelected
            ? '取消选择'
            : '全选'
        }
      >
        <div
          className={cn(
            'w-4 h-4 rounded border border-border flex items-center justify-center transition-colors',
            (isAllSelected || isPartialSelected) && 'bg-primary border-primary'
          )}
        >
          {(isAllSelected || isPartialSelected) && (
            <CheckSquare className="h-3 w-3 text-primary-foreground" />
          )}
        </div>
      </Button>
      <span>
        {isAllSelected
          ? `已全选 ${totalCount} 项`
          : isPartialSelected
          ? `已选 ${selectedCount} / ${totalCount} 项`
          : `共 ${totalCount} 项`}
      </span>
    </div>
  );
}
