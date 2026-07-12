/**
 * 我的审批任务页面
 */

'use client';

import { Card, CardContent } from '@/components/ui/card';

export default function WorkflowTasksPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">我的审批任务</h1>
        <p className="text-muted-foreground mt-1">
          与您相关的所有审批任务
        </p>
      </div>

      <Card>
        <CardContent className="p-12">
          <p className="text-muted-foreground text-center">
            审批任务列表将在这里显示
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
