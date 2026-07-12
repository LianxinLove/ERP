/**
 * 组织架构页面
 * @description 组织管理模块主页（即将推出）
 */

'use client';

import { Building2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function OrganizationPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">组织架构</h1>
        <p className="text-muted-foreground mt-1">
          管理公司组织结构、部门和员工信息
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            即将推出
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            组织架构管理模块正在开发中，敬请期待。将包含以下功能：
          </p>
          <ul className="list-disc list-inside mt-4 text-muted-foreground space-y-1">
            <li>部门管理</li>
            <li>岗位管理</li>
            <li>员工档案</li>
            <li>组织架构图</li>
            <li>员工权限分配</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
