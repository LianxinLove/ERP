'use client';

/**
 * 员工选择器组件
 *
 * @description 支持搜索的员工选择器
 *
 * @features
 * - 实时搜索
 * - 按部门筛选
 * - 显示头像和姓名
 * - 单选/多选
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { Check, Search, X, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { User } from '@/types/auth';

/**
 * 员工选择器属性
 */
interface EmployeeSelectorProps {
  /** 员工列表 */
  employees: User[];
  /** 选中的员工ID */
  value?: number | number[];
  /** 变化回调 */
  onChange?: (value: number | number[]) => void;
  /** 是否多选 */
  multiple?: boolean;
  /** 占位符 */
  placeholder?: string;
  /** 是否禁用 */
  disabled?: boolean;
  /** 类名 */
  className?: string;
}

/**
 * 员工选择器组件
 */
export function EmployeeSelector({
  employees,
  value,
  onChange,
  multiple = false,
  placeholder = '请选择员工',
  disabled = false,
  className,
}: EmployeeSelectorProps) {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  // 将value转换为Set
  const selectedIds = useCallback((): Set<number> => {
    if (multiple && Array.isArray(value)) {
      return new Set(value);
    }
    if (value && !Array.isArray(value)) {
      return new Set([value]);
    }
    return new Set();
  }, [value, multiple]);

  // 选择处理
  const handleSelect = (id: number) => {
    if (disabled) return;

    if (multiple) {
      const current = selectedIds();
      const newSelected = new Set(current);
      if (newSelected.has(id)) {
        newSelected.delete(id);
      } else {
        newSelected.add(id);
      }
      onChange?.(Array.from(newSelected));
    } else {
      onChange?.(id);
      setOpen(false);
    }
  };

  // 移除选中
  const handleRemove = (id: number) => {
    if (disabled) return;

    if (multiple && Array.isArray(value)) {
      onChange?.(value.filter((v) => v !== id));
    }
  };

  // 清空选择
  const handleClear = () => {
    if (disabled) return;
    onChange?.(multiple ? [] : 0);
  };

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // 过滤员工
  const filteredEmployees = employees.filter((emp) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      emp.username?.toLowerCase().includes(term) ||
      emp.full_name?.toLowerCase().includes(term) ||
      emp.email?.toLowerCase().includes(term)
    );
  });

  // 获取选中的员工
  const getSelectedEmployees = () => {
    const ids = selectedIds();
    return employees.filter((emp) => ids.has(emp.id));
  };

  const selectedEmployees = getSelectedEmployees();

  return (
    <div ref={containerRef} className={cn('relative', className)}>
      {/* 触发按钮 */}
      <div className="flex items-center gap-2 p-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm">
        {/* 已选择的员工标签 */}
        <div className="flex flex-wrap gap-1 flex-1">
          {selectedEmployees.length > 0 ? (
            selectedEmployees.map((emp) => (
              <span
                key={emp.id}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-sm"
              >
                {emp.full_name || emp.username}
                {!disabled && (
                  <button
                    type="button"
                    onClick={() => handleRemove(emp.id)}
                    className="p-0.5 hover:bg-blue-200 dark:hover:bg-blue-800 rounded"
                  >
                    <X className="h-3 w-3" />
                  </button>
                )}
              </span>
            ))
          ) : (
            <span className="text-sm text-gray-500 dark:text-gray-400">{placeholder}</span>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-1">
          {selectedEmployees.length > 0 && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <X className="h-4 w-4 text-gray-400" />
            </button>
          )}
          <button
            type="button"
            onClick={() => !disabled && setOpen(!open)}
            disabled={disabled}
            className={cn('p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded', disabled && 'opacity-50 cursor-not-allowed')}
          >
            <ChevronDown className={cn('h-4 w-4 transition-transform', open && 'rotate-180')} />
          </button>
        </div>
      </div>

      {/* 下拉面板 */}
      {open && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg">
          {/* 搜索框 */}
          <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200 dark:border-gray-700">
            <Search className="h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索员工..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 text-sm outline-none bg-transparent"
            />
          </div>

          {/* 员工列表 */}
          <div className="max-h-60 overflow-auto py-1">
            {filteredEmployees.length > 0 ? (
              filteredEmployees.map((emp) => {
                const isSelected = selectedIds().has(emp.id);
                return (
                  <div
                    key={emp.id}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer',
                      isSelected && 'bg-blue-50 dark:bg-blue-900/20'
                    )}
                    onClick={() => handleSelect(emp.id)}
                  >
                    {/* 多选框 */}
                    {multiple && (
                      <div className={cn(
                        'w-4 h-4 rounded border',
                        isSelected
                          ? 'bg-blue-500 border-blue-500'
                          : 'border-gray-300 dark:border-gray-600'
                      )}>
                        {isSelected && <Check className="h-3 w-3 text-white" />}
                      </div>
                    )}

                    {/* 头像 */}
                    <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-300">
                        {(emp.full_name || emp.username || '').charAt(0).toUpperCase()}
                      </span>
                    </div>

                    {/* 信息 */}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {emp.full_name || emp.username}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {emp.email}
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="px-3 py-4 text-center text-sm text-gray-500">
                未找到匹配的员工
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
