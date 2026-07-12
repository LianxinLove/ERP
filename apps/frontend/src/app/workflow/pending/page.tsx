/**
 * 我的待办任务页面
 *
 * @description 展示当前用户待处理的审批任务列表
 */

'use client';

import { useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Clock, FileText, AlertCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { workflowApi } from '@/api/workflow';
import type { WorkflowTask } from '@/types/workflow';
import Link from 'next/link';
import { toast } from 'sonner';

/**
 * 任务状态徽章变体
 */
const TaskStatusBadge = ({ status }: { status: WorkflowTask['status'] }) => {
  switch (status) {
    case 'pending':
      return <Badge variant="warning">待处理</Badge>;
    case 'approved':
      return <Badge variant="success">已通过</Badge>;
    case 'rejected':
      return <Badge variant="destructive">已拒绝</Badge>;
    case 'returned':
      return <Badge variant="secondary">已退回</Badge>;
    case 'cancelled':
      return <Badge variant="outline">已取消</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

/**
 * 紧急程度标签
 */
const UrgencyBadge = ({ dueDate }: { dueDate?: string }) => {
  if (!dueDate) return null;

  const now = new Date();
  const due = new Date(dueDate);
  const daysUntilDue = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

  if (daysUntilDue < 0) {
    return <Badge variant="destructive" className="text-xs">已超期</Badge>;
  } else if (daysUntilDue === 0) {
    return <Badge variant="destructive" className="text-xs">今日到期</Badge>;
  } else if (daysUntilDue <= 1) {
    return <Badge variant="warning" className="text-xs">1天内到期</Badge>;
  } else if (daysUntilDue <= 3) {
    return <Badge variant="info" className="text-xs">3天内到期</Badge>;
  }

  return null;
};

/**
 * 待办任务列表表格
 */
function PendingTasksTable({ tasks }: { tasks: WorkflowTask[] }) {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <FileText className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">暂无待办任务</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>任务标题</TableHead>
          <TableHead>审批节点</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead>到期时间</TableHead>
          <TableHead>状态</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {tasks.map((task) => (
          <TableRow key={task.id}>
            <TableCell className="font-medium">
              <div className="flex items-center gap-2">
                <Link
                  href={`/workflow/tasks/${task.instance_id}`}
                  className="hover:underline hover:text-primary transition-colors"
                >
                  {task.instance_title}
                </Link>
                <UrgencyBadge dueDate={task.due_date} />
              </div>
            </TableCell>
            <TableCell>{task.node_name}</TableCell>
            <TableCell>
              {format(new Date(task.created_at), 'yyyy-MM-dd HH:mm')}
            </TableCell>
            <TableCell>
              {task.due_date
                ? format(new Date(task.due_date), 'yyyy-MM-dd')
                : '-'}
            </TableCell>
            <TableCell>
              <TaskStatusBadge status={task.status} />
            </TableCell>
            <TableCell className="text-right">
              <Button variant="outline" size="sm" asChild>
                <Link href={`/workflow/tasks/${task.instance_id}`}>
                  查看详情
                </Link>
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/**
 * 加载骨架屏
 */
function PendingTasksSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>任务标题</TableHead>
          <TableHead>审批节点</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead>到期时间</TableHead>
          <TableHead>状态</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3, 4, 5].map((i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-5 w-32" /></TableCell>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-28" /></TableCell>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-16" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/**
 * 页面主体
 */
export default function PendingTasksPage() {
  const queryClient = useQueryClient();

  // 获取待办任务列表
  const {
    data: tasks,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['workflow', 'tasks', 'pending'],
    queryFn: () => workflowApi.getMyPendingTasks(),
    retry: 1,
  });

  // 定期刷新数据（每30秒）
  useEffect(() => {
    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ['workflow', 'tasks', 'pending'] });
    }, 30000);

    return () => clearInterval(interval);
  }, [queryClient]);

  // 计算超期任务数量
  const overdueCount = tasks?.filter((task) => {
    if (!task.due_date || task.status !== 'pending') return false;
    return new Date(task.due_date) < new Date();
  }).length ?? 0;

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">我的待办</h1>
          <p className="text-muted-foreground mt-1">
            查看和处理需要您审批的任务
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <Clock className="w-4 h-4 mr-2" />
          刷新
        </Button>
      </div>

      {/* 超期提醒 */}
      {overdueCount > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>有任务已超期</AlertTitle>
          <AlertDescription>
            您有 <strong>{overdueCount}</strong> 个任务已超过到期时间，请尽快处理。
          </AlertDescription>
        </Alert>
      )}

      {/* 待办任务列表 */}
      <Card>
        <CardHeader>
          <CardTitle>待办任务列表</CardTitle>
          <CardDescription>
            {tasks && tasks.length > 0
              ? `共 ${tasks.length} 个待办任务`
              : '暂无待办任务'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <PendingTasksSkeleton />
          ) : error ? (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>加载失败</AlertTitle>
              <AlertDescription>
                加载待办任务失败，请稍后重试。
                <Button
                  variant="outline"
                  size="sm"
                  className="ml-2"
                  onClick={() => refetch()}
                >
                  重试
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <PendingTasksTable tasks={tasks ?? []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
