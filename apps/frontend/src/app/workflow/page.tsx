/**
 * 审批流程模块主页
 *
 * @description 提供审批流程功能的导航入口
 */

import Link from 'next/link';
import { FileText, CheckCircle, Clock, Workflow } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

/**
 * 功能卡片组件
 */
interface FeatureCardProps {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  badge?: string;
}

function FeatureCard({ title, description, href, icon, badge }: FeatureCardProps) {
  return (
    <Link href={href}>
      <Card className="hover:shadow-lg hover:border-primary/50 transition-all cursor-pointer h-full">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                {icon}
              </div>
              <CardTitle className="text-lg">{title}</CardTitle>
            </div>
            {badge && <Badge variant="secondary">{badge}</Badge>}
          </div>
          <CardDescription className="mt-2">{description}</CardDescription>
        </CardHeader>
      </Card>
    </Link>
  );
}

/**
 * 页面主体
 */
export default function WorkflowPage() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">审批流程</h1>
        <p className="text-muted-foreground mt-1">
          管理和处理各类审批流程
        </p>
      </div>

      {/* 功能卡片网格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 我的待办 */}
        <FeatureCard
          title="我的待办"
          description="查看和处理需要您审批的任务"
          href="/workflow/pending"
          icon={<Clock className="w-6 h-6 text-primary" />}
        />

        {/* 我的已办 */}
        <FeatureCard
          title="我的已办"
          description="查看您已经处理完成的任务"
          href="/workflow/completed"
          icon={<CheckCircle className="w-6 h-6 text-primary" />}
        />

        {/* 我的申请 */}
        <FeatureCard
          title="我的申请"
          description="查看您发起的流程申请记录"
          href="/workflow/my-applications"
          icon={<FileText className="w-6 h-6 text-primary" />}
          badge="即将上线"
        />

        {/* 流程管理 */}
        <FeatureCard
          title="流程管理"
          description="管理系统中的审批流程定义"
          href="/workflow/admin"
          icon={<Workflow className="w-6 h-6 text-primary" />}
          badge="管理员"
        />

        {/* 流程统计 */}
        <FeatureCard
          title="流程统计"
          description="查看流程处理统计数据和报表"
          href="/workflow/statistics"
          icon={<Workflow className="w-6 h-6 text-primary" />}
          badge="即将上线"
        />
      </div>

      {/* 快捷操作说明 */}
      <Card>
        <CardHeader>
          <CardTitle>快捷操作</CardTitle>
          <CardDescription>常用操作指南</CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>• 点击「我的待办」查看需要您处理的任务</li>
            <li>• 在任务详情页可以进行审批通过、拒绝或退回操作</li>
            <li>• 点击「我的已办」查看历史审批记录</li>
            <li>• 点击「我的申请」查看您发起的所有申请进度</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
