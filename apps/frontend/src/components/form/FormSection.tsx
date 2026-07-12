/**
 * FormSection 表单分组组件
 * @description 使用 fieldset 对表单进行语义化分组，提供更好的可访问性和视觉组织
 */

"use client";

import React from 'react';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface FormSectionProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
}

export function FormSection({
  title,
  description,
  children,
  className,
  disabled = false,
}: FormSectionProps) {
  return (
    <fieldset
      disabled={disabled}
      className={cn('space-y-4', className)}
    >
      {(title || description) && (
        <legend className="flex flex-col gap-1 px-2 pb-2 border-b border-border">
          {title && (
            <span className="text-base font-semibold text-foreground">
              {title}
            </span>
          )}
          {description && (
            <span className="text-sm text-muted-foreground">
              {description}
            </span>
          )}
        </legend>
      )}
      {children}
    </fieldset>
  );
}

/**
 * FormRow 表单行组件
 * @description 用于组织表单字段的行布局
 */
interface FormRowProps {
  children: React.ReactNode;
  className?: string;
  cols?: 1 | 2 | 3 | 4;
}

export function FormRow({
  children,
  className,
  cols = 2,
}: FormRowProps) {
  const colsClass = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  }[cols];

  return (
    <div className={cn('grid gap-4', colsClass, className)}>
      {children}
    </div>
  );
}

/**
 * FormField 表单字段组件
 * @description 统一的表单字段包装器
 */
interface FormFieldProps {
  label?: string;
  required?: boolean;
  error?: string;
  children: React.ReactNode;
  className?: string;
  description?: string;
}

export function FormField({
  label,
  required = false,
  error,
  children,
  className,
  description,
}: FormFieldProps) {
  const child = React.Children.only(children) as React.ReactElement;

  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <Label htmlFor={child.props?.id} className="flex items-center gap-1">
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
      )}
      {React.cloneElement(child, {
        id: child.props?.id || `field-${label?.toLowerCase().replace(/\s+/g, '-')}`,
        'aria-invalid': error ? 'true' : undefined,
        'aria-describedby': error
          ? `${child.props?.id}-error`
          : description
          ? `${child.props?.id}-description`
          : undefined,
      })}
      {description && !error && (
        <p id={`${child.props?.id}-description`} className="text-xs text-muted-foreground">
          {description}
        </p>
      )}
      {error && (
        <p
          id={`${child.props?.id}-error`}
          className="text-xs text-destructive flex items-center gap-1"
          role="alert"
        >
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}

/**
 * FormActions 表单操作按钮区
 */
interface FormActionsProps {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

export function FormActions({
  children,
  align = 'right',
  className,
}: FormActionsProps) {
  const alignClass = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  }[align];

  return (
    <div className={cn('flex items-center gap-3 pt-4 border-t border-border', alignClass, className)}>
      {children}
    </div>
  );
}

/**
 * FormSectionCard 带卡片的表单分组
 */
interface FormSectionCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

export function FormSectionCard({
  title,
  description,
  children,
  className,
  collapsible = false,
  defaultCollapsed = false,
}: FormSectionCardProps) {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);

  return (
    <div className={cn('border border-border rounded-lg', className)}>
      <div
        className={cn(
          'flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30',
          collapsible && 'cursor-pointer hover:bg-muted/50 transition-colors'
        )}
        onClick={() => collapsible && setIsCollapsed(!isCollapsed)}
      >
        <div>
          <h3 className="font-semibold text-foreground">{title}</h3>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
        {collapsible && (
          <svg
            className={cn(
              'w-5 h-5 text-muted-foreground transition-transform',
              isCollapsed ? '-rotate-90' : 'rotate-0'
            )}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        )}
      </div>
      {!isCollapsed && (
        <div className="p-4 space-y-4">{children}</div>
      )}
    </div>
  );
}
