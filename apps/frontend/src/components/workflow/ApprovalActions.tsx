/**
 * 审批操作组件
 *
 * @description 提供审批操作（通过、拒绝、退回）的界面
 */

'use client';

import { useState } from 'react';
import { CheckCircle2, XCircle, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { workflowApi } from '@/api/workflow';
import type { ApproveRequest, RejectRequest, ReturnRequest } from '@/types/workflow';
import { cn } from '@/lib/utils';

// 使用简单的toast实现，后续可替换为sonner
const toast = {
  success: (message: string) => {
    console.log('Toast success:', message);
    // TODO: 集成sonner或其他toast库
    alert(message);
  },
  error: (message: string) => {
    console.error('Toast error:', message);
    alert(message);
  },
};

/**
 * 审批类型
 */
type ApprovalActionType = 'approve' | 'reject' | 'return';

/**
 * 审批操作属性
 */
export interface ApprovalActionsProps {
  /**
   * 任务ID
   */
  taskId: number;

  /**
   * 是否只读模式
   * @default false
   */
  readonly?: boolean;

  /**
   * 操作成功回调
   */
  onSuccess?: () => void;

  /**
   * 自定义类名
   */
  className?: string;

  /**
   * 按钮尺寸
   * @default 'default'
   */
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

/**
 * ApprovalActions 审批操作组件
 *
 * @description 提供审批通过、拒绝、退回的操作按钮和对话框
 *
 * @features
 * - 审批通过（可选意见）
 * - 审批拒绝（必填原因）
 * - 退回上一节点（必填原因）
 * - 操作确认对话框
 *
 * @example
 * ```tsx
 * <ApprovalActions
 *   taskId={123}
 *   onSuccess={() => {
 *     queryClient.invalidateQueries(['pending-tasks']);
 *   }}
 * />
 * ```
 */
export function ApprovalActions({
  taskId,
  readonly = false,
  onSuccess,
  className,
  size = 'default',
}: ApprovalActionsProps) {
  const [openDialog, setOpenDialog] = useState<ApprovalActionType | null>(null);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * 处理审批操作
   */
  const handleAction = async (action: ApprovalActionType) => {
    if (!comment.trim() && (action === 'reject' || action === 'return')) {
      toast.error('请填写审批意见或原因');
      return;
    }

    setIsSubmitting(true);

    try {
      switch (action) {
        case 'approve': {
          const data: ApproveRequest = {
            comment: comment.trim() || undefined,
          };
          await workflowApi.approveTask(taskId, data);
          toast.success('审批通过成功');
          break;
        }
        case 'reject': {
          const data: RejectRequest = {
            comment: comment.trim(),
          };
          await workflowApi.rejectTask(taskId, data);
          toast.success('已拒绝该申请');
          break;
        }
        case 'return': {
          const data: ReturnRequest = {
            comment: comment.trim(),
          };
          await workflowApi.returnTask(taskId, data);
          toast.success('已退回该申请');
          break;
        }
      }

      // 重置状态
      setComment('');
      setOpenDialog(null);
      onSuccess?.();
    } catch (error) {
      console.error('审批操作失败:', error);
      toast.error('操作失败，请稍后重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * 关闭对话框
   */
  // const handleClose = () => {
  //   setOpenDialog(null);
  //   setComment('');
  // };

  if (readonly) {
    return null;
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* 审批通过 */}
      <Dialog
        open={openDialog === 'approve'}
        onOpenChange={(open) => setOpenDialog(open ? 'approve' : null)}
      >
        <DialogTrigger asChild>
          <Button variant="default" size={size} className="gap-2">
            <CheckCircle2 className="w-4 h-4" />
            通过
          </Button>
        </DialogTrigger>
        <DialogContent onClose={() => setOpenDialog(null)}>
          <DialogHeader>
            <DialogTitle>审批通过</DialogTitle>
            <DialogDescription>
              确认通过该申请吗？可选择性填写审批意见。
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Textarea
              placeholder="请输入审批意见（可选）..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              maxLength={500}
            />
            <p className="text-xs text-muted-foreground mt-2 text-right">
              {comment.length}/500
            </p>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpenDialog(null)}
              disabled={isSubmitting}
            >
              取消
            </Button>
            <Button
              type="button"
              variant="default"
              onClick={() => handleAction('approve')}
              disabled={isSubmitting}
            >
              {isSubmitting ? '提交中...' : '确认通过'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 审批拒绝 */}
      <Dialog
        open={openDialog === 'reject'}
        onOpenChange={(open) => setOpenDialog(open ? 'reject' : null)}
      >
        <DialogTrigger asChild>
          <Button variant="destructive" size={size} className="gap-2">
            <XCircle className="w-4 h-4" />
            拒绝
          </Button>
        </DialogTrigger>
        <DialogContent onClose={() => setOpenDialog(null)}>
          <DialogHeader>
            <DialogTitle>审批拒绝</DialogTitle>
            <DialogDescription>
              拒绝该申请需要填写拒绝原因，请说明具体原因。
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Textarea
              placeholder="请输入拒绝原因（必填）..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              maxLength={500}
              required
            />
            <p className="text-xs text-muted-foreground mt-2 text-right">
              {comment.length}/500
            </p>
          </div>
          <DialogFooter>
            <DialogCancel disabled={isSubmitting}>取消</DialogCancel>
            <DialogAction
              onClick={() => handleAction('reject')}
              disabled={isSubmitting || !comment.trim()}
            >
              {isSubmitting ? '提交中...' : '确认拒绝'}
            </DialogAction>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 退回 */}
      <Dialog
        open={openDialog === 'return'}
        onOpenChange={(open) => setOpenDialog(open ? 'return' : null)}
      >
        <DialogTrigger asChild>
          <Button variant="outline" size={size} className="gap-2">
            <RotateCcw className="w-4 h-4" />
            退回
          </Button>
        </DialogTrigger>
        <DialogContent onClose={() => setOpenDialog(null)}>
          <DialogHeader>
            <DialogTitle>退回申请</DialogTitle>
            <DialogDescription>
              将申请退回给发起人或上一审批节点，需要填写退回原因。
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Textarea
              placeholder="请输入退回原因（必填）..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              maxLength={500}
              required
            />
            <p className="text-xs text-muted-foreground mt-2 text-right">
              {comment.length}/500
            </p>
          </div>
          <DialogFooter>
            <DialogCancel disabled={isSubmitting}>取消</DialogCancel>
            <DialogAction
              onClick={() => handleAction('return')}
              disabled={isSubmitting || !comment.trim()}
            >
              {isSubmitting ? '提交中...' : '确认退回'}
            </DialogAction>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default ApprovalActions;
