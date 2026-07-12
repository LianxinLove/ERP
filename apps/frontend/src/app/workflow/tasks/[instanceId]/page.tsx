/**
 * 流程详情/审批页面
 *
 * @description 展示流程实例详情、进度，并提供审批操作
 */

'use client';

import { useEffect, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { ArrowLeft, Calendar, User, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { WorkflowProgressViewer } from '@/components/workflow/WorkflowProgressViewer';
import { ApprovalActions } from '@/components/workflow/ApprovalActions';
import { workflowApi } from '@/api/workflow';
import type { WorkflowInstance, WorkflowProgress, WorkflowTask } from '@/types/workflow';
import Link from 'next/link';
import { useParams } from 'next/navigation';

// 使用简单的toast实现，后续可替换为sonner
const toast = {
  success: (message: string) => {
    console.log('Toast success:', message);
    // TODO: 集成sonner或其他toast库
  },
  error: (message: string) => {
    console.error('Toast error:', message);
  },
};

import { cn } from '@/lib/utils';

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
 * 实例状态文本映射
 */
const InstanceStatusText = {
  running: '进行中',
  completed: '已完成',
  rejected: '已拒绝',
  cancelled: '已取消',
};

/**
 * 流程基本信息组件
 */
function InstanceBasicInfo({ instance }: { instance: WorkflowInstance }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-2xl">{instance.title}</CardTitle>
            <CardDescription className="mt-2">
              实例编号: {instance.instance_no}
            </CardDescription>
          </div>
          <Badge variant={InstanceStatusVariant[instance.status]} className="text-sm">
            {InstanceStatusText[instance.status]}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 发起时间 */}
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">发起时间</p>
              <p className="font-medium">
                {format(new Date(instance.created_at), 'yyyy-MM-dd HH:mm')}
              </p>
            </div>
          </div>

          {/* 完成时间 */}
          {instance.completed_at && (
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">完成时间</p>
                <p className="font-medium">
                  {format(new Date(instance.completed_at), 'yyyy-MM-dd HH:mm')}
                </p>
              </div>
            </div>
          )}

          {/* 业务编号 */}
          {instance.business_key && (
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">业务编号</p>
                <p className="font-medium">{instance.business_key}</p>
              </div>
            </div>
          )}
        </div>

        {/* 表单数据展示 */}
        {instance.form_data && Object.keys(instance.form_data).length > 0 && (
          <div className="mt-6 pt-6 border-t">
            <h4 className="font-semibold mb-3">表单数据</h4>
            <div className="bg-muted/50 rounded-lg p-4">
              <pre className="text-sm whitespace-pre-wrap">
                {JSON.stringify(instance.form_data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * 加载骨架屏
 */
function DetailSkeleton() {
  return (
    <div className="space-y-6">
      {/* 返回按钮骨架 */}
      <Skeleton className="h-10 w-24" />

      {/* 基本信息骨架 */}
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>

      {/* 流程进度骨架 */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * 页面主体
 */
export default function WorkflowInstanceDetailPage() {
  const params = useParams();
  const instanceId = Number(params.instanceId);
  const queryClient = useQueryClient();
  const [currentTaskId, setCurrentTaskId] = useState<number | null>(null);

  // 获取流程实例详情
  const {
    data: instance,
    isLoading: isLoadingInstance,
    error: instanceError,
  } = useQuery({
    queryKey: ['workflow', 'instances', instanceId],
    queryFn: () => workflowApi.getInstance(instanceId),
    enabled: !isNaN(instanceId),
  });

  // 获取流程进度
  const {
    data: progress,
    isLoading: isLoadingProgress,
    error: progressError,
  } = useQuery({
    queryKey: ['workflow', 'instances', instanceId, 'progress'],
    queryFn: () => workflowApi.getInstanceProgress(instanceId),
    enabled: !isNaN(instanceId),
  });

  // 从进度中提取当前用户的待办任务
  useEffect(() => {
    if (progress?.nodes) {
      // 找到当前节点的待办任务
      const pendingTask = progress.nodes.find(
        (node) => node.node_key === progress.current_node && node.status === 'pending'
      );
      // 这里需要获取当前用户ID来判断是否是分配给当前用户的任务
      // 暂时简化处理，假设pendingTask就是当前用户的任务
      // 实际需要从auth context获取当前用户ID并对比
      if (pendingTask) {
        // 需要有一个方法来获取任务的task_id
        // 但ProgressNode中没有task_id，需要调整
      }
    }
  }, [progress]);

  // 刷新数据
  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ['workflow', 'instances', instanceId] });
    queryClient.invalidateQueries({ queryKey: ['workflow', 'instances', instanceId, 'progress'] });
  };

  // 审批成功回调
  const handleApprovalSuccess = () => {
    toast.success('审批操作成功');
    handleRefresh();
  };

  // 错误处理
  const error = instanceError || progressError;
  const isLoading = isLoadingInstance || isLoadingProgress;

  if (isNaN(instanceId)) {
    return (
      <div className="container mx-auto py-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>无效的实例ID</AlertTitle>
          <AlertDescription>
            请提供有效的流程实例ID。
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>加载失败</AlertTitle>
          <AlertDescription>
            加载流程详情失败，请稍后重试。
            <Button
              variant="outline"
              size="sm"
              className="ml-2"
              onClick={handleRefresh}
            >
              重试
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="container mx-auto py-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (!instance || !progress) {
    return (
      <div className="container mx-auto py-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>数据不存在</AlertTitle>
          <AlertDescription>
            未找到该流程实例的详细信息。
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // 判断是否可以进行审批操作
  const canApprove = instance.status === 'running' && currentTaskId !== null;

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* 返回按钮 */}
      <Button variant="ghost" asChild>
        <Link href="/workflow/pending" className="gap-2">
          <ArrowLeft className="w-4 h-4" />
          返回待办列表
        </Link>
      </Button>

      {/* 流程基本信息 */}
      <InstanceBasicInfo instance={instance} />

      {/* 审批操作区域 */}
      {canApprove && currentTaskId && (
        <Card className="border-primary/50">
          <CardHeader>
            <CardTitle className="text-lg">待您审批</CardTitle>
            <CardDescription>
              请对该申请进行审批操作
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ApprovalActions
              taskId={currentTaskId}
              onSuccess={handleApprovalSuccess}
            />
          </CardContent>
        </Card>
      )}

      {/* 流程进度 */}
      {progress && <WorkflowProgressViewer progress={progress} />}
    </div>
  );
}
