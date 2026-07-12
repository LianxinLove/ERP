/**
 * 表单字段组件
 * @description 统一的表单字段组件，包含标签、输入框、错误提示
 */

"use client";

import { ReactNode } from "react";
import { useFormContext } from "react-hook-form";
import {
  FormControl,
  FormDescription,
  FormField as FormFieldUI,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Input,
  InputProps as UIInputProps,
} from "@/components/ui/input";
import { Textarea, TextareaProps } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";

/**
 * 表单字段组件属性
 */
interface FormFieldProps {
  /** 字段名称 */
  name: string;
  /** 标签 */
  label?: string;
  /** 描述 */
  description?: string;
  /** 是否必填 */
  required?: boolean;
  /** 占位符 */
  placeholder?: string;
  /** 类名 */
  className?: string;
}

/**
 * 文本输入字段
 */
export function TextField({
  name,
  label,
  description,
  required,
  placeholder,
  className,
  ...props
}: FormFieldProps & UIInputProps) {
  return (
    <FormFieldUI
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          {label && (
            <FormLabel>
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
          )}
          <FormControl>
            <Input placeholder={placeholder} {...field} {...props} />
          </FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

/**
 * 多行文本输入字段
 */
export function TextareaField({
  name,
  label,
  description,
  required,
  placeholder,
  className,
  rows = 3,
  ...props
}: FormFieldProps & TextareaProps) {
  return (
    <FormFieldUI
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          {label && (
            <FormLabel>
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
          )}
          <FormControl>
            <Textarea
              placeholder={placeholder}
              rows={rows}
              {...field}
              {...props}
            />
          </FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

/**
 * 选择字段
 */
interface SelectFieldProps extends FormFieldProps {
  options: { label: string; value: string }[];
  placeholder?: string;
}

export function SelectField({
  name,
  label,
  description,
  required,
  placeholder = "请选择",
  options,
  className,
}: SelectFieldProps) {
  return (
    <FormFieldUI
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          {label && (
            <FormLabel>
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
          )}
          <Select onValueChange={field.onChange} defaultValue={field.value}>
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              {options.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}

/**
 * 开关字段
 */
interface SwitchFieldProps extends FormFieldProps {
  label?: string;
  description?: string;
}

export function SwitchField({
  name,
  label,
  description,
  className,
}: SwitchFieldProps) {
  return (
    <FormFieldUI
      name={name}
      render={({ field }) => (
        <FormItem className={cn("flex flex-row items-center justify-between", className)}>
          <div className="space-y-0.5">
            {label && <FormLabel>{label}</FormLabel>}
            {description && <FormDescription>{description}</FormDescription>}
          </div>
          <FormControl>
            <Switch
              checked={field.value}
              onCheckedChange={field.onChange}
            />
          </FormControl>
        </FormItem>
      )}
    />
  );
}

/**
 * 复选框字段
 */
interface CheckboxFieldProps extends FormFieldProps {
  label: string;
  description?: string;
}

export function CheckboxField({
  name,
  label,
  description,
  className,
}: CheckboxFieldProps) {
  return (
    <FormFieldUI
      name={name}
      render={({ field }) => (
        <FormItem className={cn("flex flex-row items-start space-x-2 space-y-0", className)}>
          <FormControl>
            <Checkbox
              checked={field.value}
              onCheckedChange={field.onChange}
            />
          </FormControl>
          <div className="space-y-1 leading-none">
            <FormLabel>{label}</FormLabel>
            {description && <FormDescription>{description}</FormDescription>}
          </div>
        </FormItem>
      )}
    />
  );
}

/**
 * 只读字段
 */
export function ReadOnlyField({
  name,
  label,
  className,
}: Omit<FormFieldProps, "placeholder" | "required">) {
  const form = useFormContext();
  const value = form.watch(name);

  return (
    <FormItem className={className}>
      {label && <FormLabel>{label}</FormLabel>}
      <FormControl>
        <div className="px-3 py-2 text-sm bg-muted rounded-md min-h-[2.5rem] flex items-center">
          {value || "-"}
        </div>
      </FormControl>
    </FormItem>
  );
}

/**
 * 自定义字段容器
 */
export function CustomField({
  name,
  label,
  description,
  required,
  className,
  children,
}: FormFieldProps & { children: ReactNode | ((field: any) => ReactNode) }) {
  return (
    <FormFieldUI
      name={name}
      render={({ field }) => (
        <FormItem className={className}>
          {label && (
            <FormLabel>
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
          )}
          <FormControl>{typeof children === "function" ? (children as any)(field) : children}</FormControl>
          {description && <FormDescription>{description}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
