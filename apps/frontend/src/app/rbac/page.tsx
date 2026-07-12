/**
 * 用户权限管理页面
 * @description RBAC模块主页
 */

'use client';

import Link from 'next/link';
import { Users, Shield, ShieldCheck, Database } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function RbacPage() {
  const menuItems = [
    {
      title: '角色管理',
      description: '管理系统角色和权限分配',
      icon: Shield,
      href: '/rbac/roles',
      color: 'text-blue-600',
    },
    {
      title: '权限管理',
      description: '管理系统权限列表',
      icon: ShieldCheck,
      href: '/rbac/permissions',
      color: 'text-green-600',
    },
    {
      title: '用户角色分配',
      description: '为用户分配和管理角色',
      icon: Users,
      href: '/rbac/user-roles',
      color: 'text-purple-600',
    },
    {
      title: '数据权限配置',
      description: '配置用户的数据访问范围',
      icon: Database,
      href: '/rbac/data-permissions',
      color: 'text-orange-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">用户权限管理</h1>
        <p className="text-muted-foreground mt-1">
          管理用户角色、权限分配和访问控制
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <Card className="hover:bg-muted/50 transition-colors cursor-pointer h-full">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <Icon className={`h-6 w-6 ${item.color}`} />
                    {item.title}
                  </CardTitle>
                  <CardDescription>{item.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="ghost" className="w-full">
                    进入模块 →
                  </Button>
                </CardContent>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
