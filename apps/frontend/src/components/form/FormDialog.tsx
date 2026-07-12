/**
 * 表单对话框组件
 * @description 统一的表单对话框，包含标题、表单、操作按钮
 */

"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface FormDialogProps {
  /** 是否打开 */
  open: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 标题 */
  title: string;
  /** 描述 */
  description?: string;
  /** 提交处理函数 */
  onSubmit: (data: any) => Promise<void>;
  /** 是否正在加载 */
  loading?: boolean;
  /** 取消按钮文字 */
  cancelText?: string;
  /** 确认按钮文字 */
  submitText?: string;
  /** 确认按钮类型 */
  submitVariant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  /** 是否禁用提交 */
  disabled?: boolean;
  /** 子元素（表单内容） */
  children: React.ReactNode;
}

/**
 * 表单对话框组件
 *
 * @features
 * - 统一的对话框样式
 * - 自动处理加载状态
 * - 错误处理和提示
 * - 表单验证状态检查
 *
 * @example
 * ```tsx
 * <FormDialog
 *   open={open}
 *   onClose={() => setOpen(false)}
 *   title="创建用户"
 *   onSubmit={handleSubmit}
 *   loading={loading}
 * >
 *   <UserForm />
 * </FormDialog>
 * ```
 */
export function FormDialog({
  open,
  onClose,
  title,
  description,
  onSubmit,
  loading = false,
  cancelText = "取消",
  submitText = "确定",
  submitVariant = "default",
  disabled = false,
  children,
}: FormDialogProps) {
  const [submitting, setSubmitting] = useState(false);

  /**
   * 处理提交
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 获取表单数据
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
      setSubmitting(true);
      await onSubmit(data);
      // 成功后关闭对话框
      onClose();
    } catch (error) {
      console.error("提交失败:", error);
      const message = error instanceof Error ? error.message : "操作失败";
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" onClose={onClose}>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            {description && <DialogDescription>{description}</DialogDescription>}
          </DialogHeader>

          <div className="py-4">{children}</div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={submitting || loading}
            >
              {cancelText}
            </Button>
            <Button
              type="submit"
              variant={submitVariant}
              disabled={disabled || submitting || loading}
            >
              {submitting || loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  处理中...
                </>
              ) : (
                submitText
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
