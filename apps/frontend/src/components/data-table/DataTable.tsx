/**
 * DataTable 数据表格组件
 * @description 带分页、筛选、排序的数据表格组件，支持响应式（移动端卡片视图）
 */

"use client";

import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ChevronLeft, ChevronRight, Search, SlidersHorizontal, CheckSquare, Square } from 'lucide-react';
import { cn } from '@/lib/utils';
import { MobileCardView, CompactCardView } from './MobileCardView';
import { BatchActions } from './BatchActions';

export interface Column<T> {
  id: string;
  header: string;
  cell: (row: T) => React.ReactNode;
  className?: string;
  sortable?: boolean;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  isLoading?: boolean;
  searchable?: boolean;
  searchableFields?: (keyof T)[];
  pagination?: boolean;
  pageSize?: number;
  emptyMessage?: string;
  className?: string;
  onRowClick?: (row: T) => void;
  // 批量选择功能
  selectable?: boolean;
  onSelectChange?: (selectedRows: T[]) => void;
  selectedIds?: (string | number)[];
  getId?: (row: T, index?: number) => string | number;
  // 批量操作
  batchActions?: Array<{
    label: string;
    onClick: (selectedRows: T[]) => void;
    variant?: 'default' | 'destructive' | 'outline';
    icon?: React.ReactNode;
  }>;
}

export function DataTable<T>({
  data,
  columns,
  isLoading = false,
  searchable = true,
  searchableFields = [],
  pagination = true,
  pageSize = 10,
  emptyMessage = '暂无数据',
  className,
  onRowClick,
  selectable = false,
  onSelectChange,
  selectedIds = [],
  getId = (row, index) => index ?? 0,
  batchActions = [],
}: DataTableProps<T>) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);

  // 本地选择状态（如果未传入 selectedIds）
  const [localSelectedIds, setLocalSelectedIds] = useState<(string | number)[]>([]);
  const isControlled = selectedIds.length > 0 || onSelectChange;
  const currentSelectedIds = isControlled ? selectedIds : localSelectedIds;

  // 处理行选择
  const handleRowSelect = (row: T, index: number) => {
    const rowId = getId(row, index);
    const isSelected = currentSelectedIds.includes(rowId);

    let newSelectedIds: (string | number)[];
    if (isSelected) {
      newSelectedIds = currentSelectedIds.filter(id => id !== rowId);
    } else {
      newSelectedIds = [...currentSelectedIds, rowId];
    }

    if (!isControlled) {
      setLocalSelectedIds(newSelectedIds);
    }
    onSelectChange?.(newSelectedIds.map(id =>
      data.find((row, i) => getId(row, i) === id)!
    ).filter(Boolean));
  };

  // 清除选择
  const handleClearSelection = () => {
    if (!isControlled) {
      setLocalSelectedIds([]);
    }
    onSelectChange?.([]);
  };

  // 搜索过滤
  const filteredData = React.useMemo(() => {
    if (!searchTerm || !searchableFields.length) return data;

    const lowerTerm = searchTerm.toLowerCase();
    return data.filter((row) =>
      searchableFields.some((field) => {
        const value = row[field];
        if (value === null || value === undefined) return false;
        return String(value).toLowerCase().includes(lowerTerm);
      })
    );
  }, [data, searchTerm, searchableFields]);

  // 排序
  const sortedData = React.useMemo(() => {
    if (!sortColumn) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = (a as any)[sortColumn];
      const bValue = (b as any)[sortColumn];

      if (aValue === bValue) return 0;
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      const comparison = aValue < bValue ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [filteredData, sortColumn, sortDirection]);

  // 分页
  const paginatedData = React.useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    return sortedData.slice(startIndex, startIndex + pageSize);
  }, [sortedData, currentPage, pageSize, pagination]);

  // 获取选中的行数据
  const selectedRows = currentSelectedIds.map(id =>
    data.find((row, i) => getId(row, i) === id)
  ).filter((row): row is T => row !== undefined);

  // 检查当前页是否全选
  const isCurrentPageAllSelected = paginatedData.length > 0 &&
    paginatedData.every((row, i) => currentSelectedIds.includes(getId(row, i)));

  // 检查是否有部分选中
  const isPartialSelected = paginatedData.length > 0 &&
    paginatedData.some((row, i) => currentSelectedIds.includes(getId(row, i)));

  const totalPages = pagination ? Math.ceil(sortedData.length / pageSize) : 1;

  // 处理全选/取消全选（需要在 paginatedData 定义之后）
  const handleSelectAll = () => {
    const isAllSelected = paginatedData.length > 0 &&
      paginatedData.every((row, i) => currentSelectedIds.includes(getId(row, i)));

    let newSelectedIds: (string | number)[];
    if (isAllSelected) {
      // 取消全选当前页
      newSelectedIds = currentSelectedIds.filter(id =>
        !paginatedData.some((row, i) => getId(row, i) === id)
      );
    } else {
      // 全选当前页（不重复添加）
      const pageIds = paginatedData.map((row, i) => getId(row, i));
      newSelectedIds = [...new Set([...currentSelectedIds, ...pageIds])];
    }

    if (!isControlled) {
      setLocalSelectedIds(newSelectedIds);
    }
    onSelectChange?.(newSelectedIds.map(id =>
      data.find((row, i) => getId(row, i) === id)!
    ).filter(Boolean));
  };

  const handleSort = (columnId: string) => {
    const column = columns.find((col) => col.id === columnId);
    if (!column?.sortable) return;

    if (sortColumn === columnId) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnId);
      setSortDirection('asc');
    }
  };

  const handleRowClick = (row: T) => {
    if (onRowClick) onRowClick(row);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center gap-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          <span className="text-muted-foreground">加载中...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* 搜索栏 */}
      {searchable && searchableFields.length > 0 && (
        <div className="flex items-center gap-2">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="搜索..."
              aria-label="搜索内容"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-8"
            />
          </div>

          {/* 选择状态指示 */}
          {selectable && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <button
                type="button"
                onClick={handleSelectAll}
                className={cn(
                  'flex items-center gap-1 px-2 py-1 rounded hover:bg-accent transition-colors',
                  'focus:outline-none focus:ring-2 focus:ring-ring'
                )}
                aria-label={
                  isCurrentPageAllSelected
                    ? '取消全选'
                    : '全选当前页'
                }
              >
                <div
                  className={cn(
                    'w-4 h-4 rounded border border-border flex items-center justify-center',
                    (isCurrentPageAllSelected || isPartialSelected) && 'bg-primary border-primary'
                  )}
                >
                  {(isCurrentPageAllSelected || isPartialSelected) && (
                    <CheckSquare className="h-3 w-3 text-primary-foreground" />
                  )}
                </div>
                <span>
                  {isCurrentPageAllSelected
                    ? '已全选'
                    : isPartialSelected
                    ? `已选 ${currentSelectedIds.length} 项`
                    : '全选'}
                </span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* 批量操作栏 */}
      {selectable && currentSelectedIds.length > 0 && (
        <BatchActions
          selectedCount={currentSelectedIds.length}
          totalCount={data.length}
          onClearSelection={handleClearSelection}
          customActions={batchActions.map(action => ({
            ...action,
            onClick: () => action.onClick(selectedRows),
          }))}
        />
      )}

      {/* 移动端卡片视图 - 小屏幕显示 */}
      <div className="lg:hidden">
        <MobileCardView
          data={paginatedData}
          columns={columns}
          onRowClick={onRowClick}
          emptyMessage={emptyMessage}
        />
      </div>

      {/* 桌面端表格视图 - 大屏幕显示 */}
      <div className="hidden lg:block rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {/* 选择列 */}
              {selectable && (
                <TableHead className="w-12">
                  <button
                    type="button"
                    onClick={handleSelectAll}
                    className={cn(
                      'flex items-center justify-center w-full',
                      'focus:outline-none focus:ring-2 focus:ring-ring rounded'
                    )}
                    aria-label={
                      isCurrentPageAllSelected
                        ? '取消全选当前页'
                        : '全选当前页'
                    }
                  >
                    <div
                      className={cn(
                        'w-4 h-4 rounded border border-border flex items-center justify-center',
                        (isCurrentPageAllSelected || isPartialSelected) && 'bg-primary border-primary'
                      )}
                    >
                      {(isCurrentPageAllSelected || isPartialSelected) && (
                        <CheckSquare className="h-3 w-3 text-primary-foreground" />
                      )}
                    </div>
                  </button>
                </TableHead>
              )}
              {columns.map((column) => (
                <TableHead
                  key={column.id}
                  className={cn(
                    column.sortable && 'cursor-pointer hover:bg-muted/50',
                    column.className
                  )}
                  onClick={() => column.sortable && handleSort(column.id)}
                  aria-sort={
                    sortColumn === column.id
                      ? sortDirection === 'asc'
                        ? 'ascending'
                        : 'descending'
                      : undefined
                  }
                >
                  <div className="flex items-center gap-1">
                    {column.header}
                    {column.sortable && (
                      <span className="text-muted-foreground" aria-hidden="true">
                        {sortColumn === column.id ? (
                          sortDirection === 'asc' ? '↑' : '↓'
                        ) : (
                          '↕'
                        )}
                      </span>
                    )}
                  </div>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={columns.length + (selectable ? 1 : 0)}
                  className="h-24 text-center text-muted-foreground"
                >
                  {emptyMessage}
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, index) => {
                const rowId = getId(row, index);
                const isSelected = currentSelectedIds.includes(rowId);

                return (
                  <TableRow
                    key={index}
                    onClick={(e) => {
                      // 如果点击的是复选框，不触发行的点击
                      if ((e.target as HTMLElement).closest('input[type="checkbox"]')) {
                        return;
                      }
                      handleRowClick(row);
                    }}
                    className={cn(
                      onRowClick && 'cursor-pointer',
                      isSelected && 'bg-muted/30',
                      'hover:bg-muted/50 transition-colors'
                    )}
                    data-clickable={onRowClick ? 'true' : undefined}
                    data-selected={isSelected ? 'true' : undefined}
                  >
                    {/* 选择列 */}
                    {selectable && (
                      <TableCell className="w-12">
                        <div className="flex items-center justify-center">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => handleRowSelect(row, index)}
                            className="w-4 h-4 rounded border-border cursor-pointer focus:ring-2 focus:ring-ring"
                            aria-label={`选择第 ${index + 1} 行`}
                          />
                        </div>
                      </TableCell>
                    )}
                    {columns.map((column) => (
                      <TableCell key={column.id} className={column.className}>
                        {column.cell(row)}
                      </TableCell>
                    ))}
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* 分页 */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            共 {sortedData.length} 条记录，第 {currentPage} / {totalPages} 页
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              aria-label="上一页"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <div className="flex items-center gap-1" role="navigation" aria-label="分页">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? 'default' : 'outline'}
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setCurrentPage(pageNum)}
                    aria-label={`第 ${pageNum} 页`}
                    aria-current={currentPage === pageNum ? 'page' : undefined}
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              aria-label="下一页"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 数据表格筛选组件
 */
interface DataTableFilterProps {
  filters: Array<{
    id: string;
    label: string;
    options: Array<{ value: string; label: string }>;
    value?: string;
    onChange: (value: string) => void;
  }>;
}

export function DataTableFilter({ filters }: DataTableFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
      {filters.map((filter) => (
        <Select
          key={filter.id}
          value={filter.value}
          onValueChange={filter.onChange}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder={filter.label} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部</SelectItem>
            {filter.options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ))}
    </div>
  );
}
