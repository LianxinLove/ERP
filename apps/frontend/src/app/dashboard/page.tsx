/**
 * Dashboard页面
 *
 * @description ERP系统主仪表板 - 现代化设计
 */

'use client';

import { useAuth } from '@/store/auth/AuthContext';
import {
  LayoutDashboard,
  ShoppingCart,
  FileText,
  Package,
  DollarSign,
  Users,
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export default function DashboardPage() {
  const { user } = useAuth();

  const statsCards = [
    {
      title: '总销售额',
      value: '¥128,430',
      change: '+12.5%',
      changeType: 'positive',
      icon: TrendingUp,
      color: 'text-emerald-600 dark:text-emerald-400',
      bgColor: 'bg-emerald-500/10 dark:bg-emerald-500/20',
      borderColor: 'border-emerald-200 dark:border-emerald-800',
      href: '/sales',
      description: '较上月增长',
    },
    {
      title: '采购订单',
      value: '45',
      change: '+3',
      changeType: 'positive',
      icon: ShoppingCart,
      color: 'text-cyan-600 dark:text-cyan-400',
      bgColor: 'bg-cyan-500/10 dark:bg-cyan-500/20',
      borderColor: 'border-cyan-200 dark:border-cyan-800',
      href: '/purchase/orders',
      description: '本月新增',
    },
    {
      title: '待审批',
      value: '12',
      change: '待处理',
      changeType: 'warning',
      icon: Activity,
      color: 'text-amber-600 dark:text-amber-400',
      bgColor: 'bg-amber-500/10 dark:bg-amber-500/20',
      borderColor: 'border-amber-200 dark:border-amber-800',
      href: '/workflow/pending',
      description: '需要您处理',
    },
    {
      title: '员工数',
      value: '156',
      change: '+2',
      changeType: 'positive',
      icon: Users,
      color: 'text-purple-600 dark:text-purple-400',
      bgColor: 'bg-purple-500/10 dark:bg-purple-500/20',
      borderColor: 'border-purple-200 dark:border-purple-800',
      href: '/organization',
      description: '本月新增',
    },
  ];

  const quickActions = [
    {
      title: '销售管理',
      description: '客户管理、销售订单、退货处理',
      icon: FileText,
      href: '/sales',
      gradient: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-gradient-to-br from-blue-500/10 to-cyan-500/10',
      badge: '8',
    },
    {
      title: '采购管理',
      description: '供应商管理、采购订单、申请审批',
      icon: ShoppingCart,
      href: '/purchase',
      gradient: 'from-emerald-500 to-green-500',
      bgColor: 'bg-gradient-to-br from-emerald-500/10 to-green-500/10',
      badge: '5',
    },
    {
      title: '库存管理',
      description: '产品管理、库存查询、出入库记录',
      icon: Package,
      href: '/inventory',
      gradient: 'from-amber-500 to-orange-500',
      bgColor: 'bg-gradient-to-br from-amber-500/10 to-orange-500/10',
      badge: '3',
    },
    {
      title: '财务管理',
      description: '科目管理、应收应付、收付款记录',
      icon: DollarSign,
      href: '/finance',
      gradient: 'from-purple-500 to-pink-500',
      bgColor: 'bg-gradient-to-br from-purple-500/10 to-pink-500/10',
      badge: '12',
    },
  ];

  const recentActivities = [
    {
      type: 'order',
      title: '新销售订单',
      description: '客户A提交了新的销售订单',
      time: '5分钟前',
      amount: '¥12,500',
      status: 'pending',
    },
    {
      type: 'approval',
      title: '采购申请待审批',
      description: 'IT设备采购申请需要您的审批',
      time: '15分钟前',
      amount: '¥8,800',
      status: 'warning',
    },
    {
      type: 'payment',
      title: '收款到账',
      description: '收到客户B付款',
      time: '1小时前',
      amount: '¥10,000',
      status: 'success',
    },
    {
      type: 'workflow',
      title: '流程完成',
      description: '采购申请审批流程已完成',
      time: '2小时前',
      amount: '¥5,200',
      status: 'success',
    },
  ];

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'order':
        return <ShoppingCart className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />;
      case 'approval':
        return <Activity className="h-5 w-5 text-amber-600 dark:text-amber-400" />;
      case 'payment':
        return <DollarSign className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />;
      case 'workflow':
        return <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />;
      default:
        return <Activity className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 border-emerald-200 dark:border-emerald-800 dark:text-emerald-400">已完成</Badge>;
      case 'warning':
        return <Badge variant="outline" className="bg-amber-500/10 text-amber-600 border-amber-200 dark:border-amber-800 dark:text-amber-400">待处理</Badge>;
      case 'pending':
        return <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-200 dark:border-blue-800 dark:text-blue-400">进行中</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8 w-full">
      {/* 欢迎信息 - 增强设计 */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
              仪表盘
            </h1>
            <p className="text-muted-foreground mt-2 text-lg">
              欢迎回来，{user?.full_name || user?.username}
            </p>
          </div>
          <Button size="lg" className="gap-2 shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-all duration-300">
            <LayoutDashboard className="h-5 w-5" />
            快速操作
          </Button>
        </div>
      </div>

      {/* 统计卡片 - 现代化设计 */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 lg:gap-6">
        {statsCards.map((card) => (
          <Link key={card.title} href={card.href} className="group">
            <Card className={cn(
              'hover:shadow-xl hover:shadow-black/5 dark:hover:shadow-black/20',
              'transition-all duration-300 ease-out',
              'border-2 hover:border-primary/20',
              'cursor-pointer h-full overflow-hidden',
              'relative'
            )}>
              {/* 装饰性背景 */}
              <div className={cn(
                'absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500',
                card.bgColor
              )} />

              <CardHeader className="relative flex flex-row items-center justify-between pb-3">
                <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  {card.title}
                </CardTitle>
                <div className={cn(
                  'p-3 rounded-xl transition-transform duration-300 group-hover:scale-110',
                  card.bgColor
                )}>
                  <card.icon className={cn('h-5 w-5', card.color)} />
                </div>
              </CardHeader>
              <CardContent className="relative">
                <div className="flex items-baseline justify-between">
                  <div className="text-3xl font-bold tracking-tight">{card.value}</div>
                  <div className={cn(
                    'flex items-center gap-1 text-sm font-medium',
                    card.changeType === 'positive' ? 'text-emerald-600 dark:text-emerald-400' :
                    card.changeType === 'warning' ? 'text-amber-600 dark:text-amber-400' :
                    'text-muted-foreground'
                  )}>
                    {card.changeType === 'positive' && <ArrowUpRight className="h-4 w-4" />}
                    {card.changeType === 'warning' && <Activity className="h-4 w-4" />}
                    {card.changeType === 'negative' && <ArrowDownRight className="h-4 w-4" />}
                    {card.change}
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2 font-medium">
                  {card.description}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* 快捷入口 - 现代卡片设计 */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold tracking-tight">快捷入口</h2>
          <Button variant="ghost" className="gap-2">
            查看全部
            <ArrowUpRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href}>
              <Card className={cn(
                'hover:shadow-xl hover:shadow-black/5 dark:hover:shadow-black/20',
                'transition-all duration-300 ease-out',
                'border-2 hover:border-primary/20',
                'cursor-pointer h-full group overflow-hidden',
                'relative'
              )}>
                {/* 渐变背景 */}
                <div className={cn(
                  'absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500',
                  action.bgColor
                )} />

                <CardContent className="relative p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className={cn(
                      'p-4 rounded-2xl bg-gradient-to-br',
                      action.gradient,
                      'text-white shadow-lg shadow-primary/25',
                      'transition-transform duration-300 group-hover:scale-110',
                      'group-hover:rotate-3'
                    )}>
                      <action.icon className="h-6 w-6" />
                    </div>
                    {action.badge && (
                      <Badge variant="secondary" className="text-xs">
                        {action.badge}
                      </Badge>
                    )}
                  </div>
                  <h3 className="font-bold text-lg mb-2 group-hover:text-primary transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {action.description}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* 最近活动 - 现代列表设计 */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold tracking-tight">最近活动</h2>
          <Button variant="ghost" className="gap-2">
            查看全部
            <ArrowUpRight className="h-4 w-4" />
          </Button>
        </div>
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {recentActivities.map((activity, index) => (
                <div
                  key={index}
                  className={cn(
                    'flex items-center gap-4 p-4 lg:p-5',
                    'hover:bg-muted/50 transition-colors duration-200',
                    'group cursor-pointer'
                  )}
                >
                  <div className={cn(
                    'flex h-12 w-12 items-center justify-center rounded-xl',
                    'transition-transform duration-300 group-hover:scale-110',
                    'bg-muted/80'
                  )}>
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold truncate group-hover:text-primary transition-colors">
                        {activity.title}
                      </p>
                      {getStatusBadge(activity.status)}
                    </div>
                    <p className="text-sm text-muted-foreground truncate">
                      {activity.description}
                    </p>
                  </div>
                  <div className="text-right flex flex-col items-end gap-1">
                    <div className="font-semibold text-foreground">
                      {activity.amount}
                    </div>
                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                      {activity.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
