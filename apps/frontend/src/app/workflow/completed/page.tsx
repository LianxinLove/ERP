/**
 * 我的已办任务页面
 *
 * @description 展示当前用户已处理完成的审批任务列表
 */

'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { FileText, CheckCircle2, XCircle, RotateCcw, AlertCircle } from 'lucide-react';
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
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { workflowApi } from '@/api/workflow';
import type { WorkflowTask } from '@/types/workflow';
import Link from 'next/link';

/**
 * 任务状态筛选
 */
type TaskStatusFilter = 'all' | 'approved' | 'rejected' | 'returned';

/**
 * 任务状态筛选配置
 */
const STATUS_FILTERS: Record<TaskStatusFilter, { label: string; status?: WorkflowTask['status'] }> = {
  all: { label: '全部' },
  approved: { label: '已通过', status: 'approved' },
  rejected: { label: '已拒绝', status: 'rejected' },
  returned: { label: '已退回', status: 'returned' },
};

/**
 * 任务状态图标
 */
const StatusIcon = ({ status }: { status: WorkflowTask['status'] }) => {
  switch (status) {
    case 'approved':
      return <CheckCircle2 className="w-4 h-4 text-green-500" />;
    case 'rejected':
      return <XCircle className="w-4 h-4 text-red-500" />;
    case 'returned':
      return <RotateCcw className="w-4 h-4 text-orange-500" />;
    case 'cancelled':
      return <XCircle className="w-4 h-4 text-gray-500" />;
    default:
      return null;
  }
};

/**
 * 任务状态徽章
 */
const TaskStatusBadge = ({ status }: { status: WorkflowTask['status'] }) => {
  switch (status) {
    case 'approved':
      return (
        <Badge variant="success" className="gap-1">
          <StatusIcon status={status} />
          已通过
        </Badge>
      );
    case 'rejected':
      return (
        <Badge variant="destructive" className="gap-1">
          <StatusIcon status={status} />
          已拒绝
        </Badge>
      );
    case 'returned':
      return (
        <Badge variant="secondary" className="gap-1">
          <StatusIcon status={status} />
          已退回
        </Badge>
      );
    case 'cancelled':
      return (
        <Badge variant="outline" className="gap-1">
          <StatusIcon status={status} />
          已取消
        </Badge>
      );
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

/**
 * 已办任务列表表格
 */
function CompletedTasksTable({ tasks }: { tasks: WorkflowTask[] }) {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <FileText className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">暂无已办任务</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>任务标题</TableHead>
          <TableHead>审批节点</TableHead>
          <TableHead>处理时间</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead>处理结果</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {tasks.map((task) => (
          <TableRow key={task.id}>
            <TableCell className="font-medium">
              <Link
                href={`/workflow/tasks/${task.instance_id}`}
                className="hover:underline hover:text-primary transition-colors"
              >
                {task.instance_title}
              </Link>
            </TableCell>
            <TableCell>{task.node_name}</TableCell>
            <TableCell>
              {task.completed_at
                ? format(new Date(task.completed_at), 'yyyy-MM-dd HH:mm')
                : '-'}
            </TableCell>
            <TableCell>
              {format(new Date(task.created_at), 'yyyy-MM-dd HH:mm')}
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
function CompletedTasksSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>任务标题</TableHead>
          <TableHead>审批节点</TableHead>
          <TableHead>处理时间</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead>处理结果</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3, 4, 5].map((i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-5 w-32" /></TableCell>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-28" /></TableCell>
            <TableCell><Skeleton className="h-5 w-28" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
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
export default function CompletedTasksPage() {
  const [activeFilter, setActiveFilter] = useState<TaskStatusFilter>('all');

  // 注意：这里假设后端提供了获取已办任务的API
  // 实际上需要根据后端API调整或扩展
  const {
    data: tasks = [],
    isLoading,
    error,
    refetch,
  } = useQuery<WorkflowTask[]>({
    queryKey: ['workflow', 'tasks', 'completed', activeFilter],
    queryFn: async () => {
      // TODO: 后端需要添加获取已办任务的API
      // 这里先返回空数组，等待后端实现
      console.warn('已办任务API尚未实现');
      return [];
    },
    retry: 1,
  });

  // 根据筛选条件过滤任务
  const filteredTasks = tasks.filter((task) => {
    if (activeFilter === 'all') return true;
    return task.status === STATUS_FILTERS[activeFilter].status;
  });

  // 计算各状态任务数量
  const statusCounts = {
    all: tasks.length,
    approved: tasks.filter((t) => t.status === 'approved').length,
    rejected: tasks.filter((t) => t.status === 'rejected').length,
    returned: tasks.filter((t) => t.status === 'returned').length,
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">我的已办</h1>
        <p className="text-muted-foreground mt-1">
          查看您已经处理完成的审批任务
        </p>
      </div>

      {/* 已办任务列表 */}
      <Card>
        <CardHeader>
          <CardTitle>已办任务列表</CardTitle>
          <CardDescription>
            {tasks.length > 0
              ? `共处理了 ${tasks.length} 个任务`
              : '暂无已办任务'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <CompletedTasksSkeleton />
          ) : error ? (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>加载失败</AlertTitle>
              <AlertDescription>
                加载已办任务失败，请稍后重试。
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
            <Tabs value={activeFilter} onValueChange={(v) => setActiveFilter(v as TaskStatusFilter)}>
              <TabsList className="mb-4">
                {Object.entries(STATUS_FILTERS).map(([key, { label }]) => (
                  <TabsTrigger key={key} value={key}>
                    {label} ({statusCounts[key as TaskStatusFilter]})
                  </TabsTrigger>
                ))}
              </TabsList>
              <TabsContent value={activeFilter} className="mt-0">
                <CompletedTasksTable tasks={filteredTasks} />
              </TabsContent>
            </Tabs>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
