/**
 * 流程进度查看组件
 *
 * @description 可视化展示审批流程的进度状态
 */

import { format } from 'date-fns';
import { CheckCircle2, Clock, XCircle, RotateCcw, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { WorkflowProgress, ProgressNode, WorkflowApproval } from '@/types/workflow';
import { cn } from '@/lib/utils';

/**
 * 节点状态图标映射
 */
const StatusIcon = {
  pending: Clock,
  approved: CheckCircle2,
  rejected: XCircle,
  returned: RotateCcw,
  cancelled: XCircle,
};

/**
 * 节点状态颜色映射
 */
const StatusColor = {
  pending: 'text-yellow-600 dark:text-yellow-400',
  approved: 'text-green-600 dark:text-green-400',
  rejected: 'text-red-600 dark:text-red-400',
  returned: 'text-orange-600 dark:text-orange-400',
  cancelled: 'text-gray-600 dark:text-gray-400',
};

/**
 * 实例状态变体映射
 */
const InstanceStatusVariant = {
  running: 'info' as const,
  completed: 'success' as const,
  rejected: 'destructive' as const,
  cancelled: 'secondary' as const,
};

/**
 * 审批操作文本映射
 */
const ActionText = {
  approve: '通过',
  reject: '拒绝',
  return: '退回',
};

/**
 * 流程节点项组件
 */
interface ProgressNodeItemProps {
  node: ProgressNode;
  isActive: boolean;
  isLast: boolean;
}

function ProgressNodeItem({ node, isActive, isLast }: ProgressNodeItemProps) {
  const Icon = StatusIcon[node.status];
  const iconColor = StatusColor[node.status];

  return (
    <div className="relative">
      {/* 节点内容 */}
      <div className="flex items-start gap-3">
        {/* 图标 */}
        <div
          className={cn(
            'flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full border-2 bg-background',
            isActive && 'ring-2 ring-ring',
            node.status === 'approved' && 'border-green-500',
            node.status === 'pending' && 'border-yellow-500',
            node.status === 'rejected' && 'border-red-500',
            node.status === 'returned' && 'border-orange-500'
          )}
        >
          <Icon className={cn('w-4 h-4', iconColor)} />
        </div>

        {/* 节点信息 */}
        <div className="flex-1 min-w-0 pt-1">
          <div className="flex items-center justify-between gap-2">
            <p className="font-medium text-sm">{node.node_name}</p>
            <Badge variant={node.status === 'approved' ? 'success' : node.status === 'pending' ? 'warning' : 'destructive'}>
              {node.status === 'approved' && '已通过'}
              {node.status === 'pending' && '待审批'}
              {node.status === 'rejected' && '已拒绝'}
              {node.status === 'returned' && '已退回'}
              {node.status === 'cancelled' && '已取消'}
            </Badge>
          </div>

          {/* 处理人信息 */}
          {node.assignee_name && (
            <p className="text-xs text-muted-foreground mt-1">
              处理人: {node.assignee_name}
            </p>
          )}

          {/* 时间信息 */}
          {node.completed_at ? (
            <p className="text-xs text-muted-foreground mt-1">
              完成时间: {format(new Date(node.completed_at), 'yyyy-MM-dd HH:mm')}
            </p>
          ) : node.created_at && (
            <p className="text-xs text-muted-foreground mt-1">
              创建时间: {format(new Date(node.created_at), 'yyyy-MM-dd HH:mm')}
            </p>
          )}
        </div>
      </div>

      {/* 连接线 */}
      {!isLast && (
        <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-border" style={{ height: 'calc(100% - 2rem)' }}>
          <ChevronRight className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground/50" />
        </div>
      )}
    </div>
  );
}

/**
 * 审批记录项组件
 */
interface ApprovalRecordItemProps {
  approval: WorkflowApproval;
}

function ApprovalRecordItem({ approval }: ApprovalRecordItemProps) {
  return (
    <div className="border-b last:border-0 py-3 last:pb-0">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm">{approval.approver_name}</span>
          <Badge
            variant={approval.action === 'approve' ? 'success' : 'destructive'}
            className="text-xs"
          >
            {ActionText[approval.action]}
          </Badge>
        </div>
        <span className="text-xs text-muted-foreground">
          {format(new Date(approval.created_at), 'yyyy-MM-dd HH:mm')}
        </span>
      </div>

      {/* 审批意见 */}
      {approval.comment && (
        <p className="text-sm text-muted-foreground mt-2 bg-muted/50 rounded p-2">
          {approval.comment}
        </p>
      )}
    </div>
  );
}

/**
 * 流程进度查看器属性
 */
export interface WorkflowProgressViewerProps {
  /**
   * 流程进度数据
   */
  progress: WorkflowProgress;

  /**
   * 是否显示审批记录
   * @default true
   */
  showApprovals?: boolean;

  /**
   * 自定义类名
   */
  className?: string;
}

/**
 * WorkflowProgressViewer 流程进度查看组件
 *
 * @description 可视化展示审批流程的进度状态，包括节点进度和审批记录
 *
 * @features
 * - 时间轴式节点展示
 * - 当前节点高亮
 * - 审批记录列表
 * - 实例状态标识
 *
 * @example
 * ```tsx
 * <WorkflowProgressViewer progress={progressData} />
 * ```
 */
export function WorkflowProgressViewer({
  progress,
  showApprovals = true,
  className,
}: WorkflowProgressViewerProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* 实例基本信息 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">{progress.title}</CardTitle>
            <Badge variant={InstanceStatusVariant[progress.status]}>
              {progress.status === 'running' && '进行中'}
              {progress.status === 'completed' && '已完成'}
              {progress.status === 'rejected' && '已拒绝'}
              {progress.status === 'cancelled' && '已取消'}
            </Badge>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>编号: {progress.instance_no}</span>
            {progress.current_node && <span>当前节点: {progress.current_node}</span>}
          </div>
        </CardHeader>
      </Card>

      {/* 流程节点进度 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">流程进度</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-4">
              {progress.nodes.map((node, index) => {
                const isActive = node.node_key === progress.current_node;
                const isLast = index === progress.nodes.length - 1;
                return (
                  <ProgressNodeItem
                    key={node.node_key}
                    node={node}
                    isActive={isActive}
                    isLast={isLast}
                  />
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* 审批记录 */}
      {showApprovals && progress.approvals.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">审批记录</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px] pr-4">
              <div className="space-y-0">
                {progress.approvals.map((approval) => (
                  <ApprovalRecordItem key={approval.id} approval={approval} />
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
