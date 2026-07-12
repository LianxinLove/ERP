/**
 * 系统设置页面
 * @description 系统设置模块主页，包含各种设置的入口
 */

'use client';

import Link from 'next/link';
import { Settings, User, Bell, Shield, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { usePermission } from '@/store/permission/PermissionContext';

interface SettingItem {
  title: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  requiredPermission?: string;
}

export default function SettingsPage() {
  const { hasPermission } = usePermission();

  const settingItems: SettingItem[] = [
    {
      title: '个人设置',
      description: '管理您的个人信息、密码和偏好设置',
      href: '/settings/profile',
      icon: <User className='h-5 w-5' />,
    },
    {
      title: '通知设置',
      description: '配置通知接收方式和免打扰时间',
      href: '/settings/notifications',
      icon: <Bell className='h-5 w-5' />,
    },
    {
      title: '系统设置',
      description: '配置系统参数和全局设置（需要管理员权限）',
      href: '/settings/system',
      icon: <Shield className='h-5 w-5' />,
      requiredPermission: 'system.config',
    },
  ];

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-3xl font-bold tracking-tight'>系统设置</h1>
        <p className='text-muted-foreground mt-1'>
          配置系统参数和个人偏好设置
        </p>
      </div>

      <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
        {settingItems.map((item) => {
          // 检查权限
          if (item.requiredPermission && !hasPermission(item.requiredPermission) && !hasPermission('admin')) {
            return null;
          }

          return (
            <Link key={item.href} href={item.href}>
              <Card className='transition-all hover:shadow-md hover:border-primary/20 cursor-pointer h-full'>
                <CardHeader>
                  <div className='flex items-center justify-between'>
                    <div className='flex items-center gap-3'>
                      <div className='w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary'>
                        {item.icon}
                      </div>
                      <CardTitle className='text-base'>{item.title}</CardTitle>
                    </div>
                    <ChevronRight className='h-5 w-5 text-muted-foreground' />
                  </div>
                  <CardDescription className='mt-2'>{item.description}</CardDescription>
                </CardHeader>
              </Card>
            </Link>
          );
        })}
      </div>

      {/* 快速操作提示 */}
      <Card className='bg-muted/50'>
        <CardContent className='pt-6'>
          <div className='flex items-start gap-3'>
            <Settings className='h-5 w-5 text-muted-foreground mt-0.5' />
            <div className='text-sm text-muted-foreground'>
              <p>提示：部分设置更改可能需要重新登录才能生效。如果您在修改设置后遇到问题，请尝试清除浏览器缓存或重新登录。</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
