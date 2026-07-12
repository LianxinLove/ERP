'use client';

/**
 * 部门选择器组件
 *
 * @description 树形结构的部门选择器
 *
 * @features
 * - 树形展示
 * - 展开/收起
 * - 搜索过滤
 * - 单选/多选
 */

import { useState, useCallback } from 'react';
import { ChevronDown, ChevronRight, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DepartmentTree } from '@/types/organization';

/**
 * 部门选择器属性
 */
interface DepartmentSelectorProps {
  /** 部门树数据 */
  departments: DepartmentTree[];
  /** 选中的部门ID */
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
 * 部门树节点组件
 */
interface DepartmentNodeProps {
  department: DepartmentTree;
  level: number;
  selectedIds: Set<number>;
  onSelect: (id: number) => void;
  multiple?: boolean;
}

function DepartmentNode({ department, level, selectedIds, onSelect, multiple }: DepartmentNodeProps) {
  const [expanded, setExpanded] = useState(level < 2); // 默认展开前两层
  const hasChildren = department.children.length > 0;
  const isSelected = selectedIds.has(department.id);

  return (
    <div>
      <div
        className={cn(
          'flex items-center gap-1 py-1.5 px-2 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800',
          isSelected && 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onSelect(department.id)}
      >
        {/* 展开/收起按钮 */}
        {hasChildren ? (
          <button
            type="button"
            className="p-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
          >
            {expanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : (
          <span className="w-5 h-5" />
        )}

        {/* 多选框 */}
        {multiple && (
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => onSelect(department.id)}
            className="rounded"
            onClick={(e) => e.stopPropagation()}
          />
        )}

        {/* 部门名称 */}
        <span className="text-sm">{department.name}</span>
      </div>

      {/* 子部门 */}
      {hasChildren && expanded && (
        <div>
          {department.children.map((child) => (
            <DepartmentNode
              key={child.id}
              department={child}
              level={level + 1}
              selectedIds={selectedIds}
              onSelect={onSelect}
              multiple={multiple}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * 部门选择器组件
 */
export function DepartmentSelector({
  departments,
  value,
  onChange,
  multiple = false,
  placeholder = '请选择部门',
  disabled = false,
  className,
}: DepartmentSelectorProps) {
  const [open, setOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredDepartments, setFilteredDepartments] = useState(departments);

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

  // 获取选中的部门名称
  const getSelectedNames = () => {
    const ids = selectedIds();
    if (ids.size === 0) return placeholder;

    const names: string[] = [];
    const findNames = (deps: DepartmentTree[]) => {
      for (const dept of deps) {
        if (ids.has(dept.id)) {
          names.push(dept.name);
        }
        if (dept.children.length > 0) {
          findNames(dept.children);
        }
      }
    };
    findNames(departments);

    return names.join(', ');
  };

  // 搜索过滤
  const handleSearch = (term: string) => {
    setSearchTerm(term);
    if (!term) {
      setFilteredDepartments(departments);
      return;
    }

    const filter = (deps: DepartmentTree[]): DepartmentTree[] => {
      const result: DepartmentTree[] = [];
      for (const dept of deps) {
        if (dept.name.toLowerCase().includes(term.toLowerCase())) {
          result.push(dept);
        } else if (dept.children.length > 0) {
          const filteredChildren = filter(dept.children);
          if (filteredChildren.length > 0) {
            result.push({ ...dept, children: filteredChildren });
          }
        }
      }
      return result;
    };

    setFilteredDepartments(filter(departments));
  };

  return (
    <div className={cn('relative', className)}>
      {/* 触发按钮 */}
      <button
        type="button"
        className={cn(
          'w-full flex items-center justify-between px-3 py-2 text-left bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onClick={() => !disabled && setOpen(!open)}
        disabled={disabled}
      >
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {getSelectedNames()}
        </span>
        <ChevronDown className={cn('h-4 w-4 transition-transform', open && 'rotate-180')} />
      </button>

      {/* 下拉面板 */}
      {open && (
        <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg">
          {/* 搜索框 */}
          <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200 dark:border-gray-700">
            <Search className="h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="搜索部门..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="flex-1 text-sm outline-none bg-transparent"
            />
          </div>

          {/* 部门树 */}
          <div className="max-h-60 overflow-auto py-1">
            {filteredDepartments.length > 0 ? (
              filteredDepartments.map((dept) => (
                <DepartmentNode
                  key={dept.id}
                  department={dept}
                  level={0}
                  selectedIds={selectedIds()}
                  onSelect={handleSelect}
                  multiple={multiple}
                />
              ))
            ) : (
              <div className="px-3 py-4 text-center text-sm text-gray-500">
                未找到匹配的部门
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
