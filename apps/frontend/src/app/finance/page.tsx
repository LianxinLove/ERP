/**
 * 财务管理页面
 * @description 财务模块主页，包含导航和财务功能
 */

'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  FileText,
  CreditCard,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Settings,
  Plus,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { financeApi } from '@/api/finance';
import type { FinanceSummary } from '@/types/finance';

export default function FinancePage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');

  // 导航菜单项
  const navItems = [
    { id: 'overview', label: '财务概览', icon: LayoutDashboard },
    { id: 'receivables', label: '应收账款', icon: TrendingUp },
    { id: 'payables', label: '应付账款', icon: TrendingDown },
    { id: 'payments', label: '收付款记录', icon: CreditCard },
    { id: 'accounts', label: '会计科目', icon: FileText },
  ];

  // 获取财务汇总数据
  const { data: summary, isLoading: summaryLoading } = useQuery<FinanceSummary>({
    queryKey: ['finance-summary'],
    queryFn: financeApi.getFinanceSummary,
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">财务管理</h1>
          <p className="text-muted-foreground mt-1">
            管理财务科目、应收应付账款和收付款记录
          </p>
        </div>
      </div>

      {/* 子导航标签页 */}
      <div className="flex gap-2 border-b">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => {
                if (item.id === 'overview') {
                  setActiveTab('overview');
                } else {
                  router.push(`/finance/${item.id}`);
                }
              }}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
                activeTab === item.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* 概览内容 */}
      {activeTab === 'overview' && (
        <>
          {/* 统计卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* 应收账款 */}
            <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push('/finance/receivables')}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">应收账款</CardTitle>
                <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                  <TrendingUp className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summaryLoading ? '...' : formatCurrency(summary?.total_receivable || 0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  逾期 {summary?.overdue_receivable_count || 0} 笔
                </p>
              </CardContent>
            </Card>

            {/* 应付账款 */}
            <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push('/finance/payables')}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">应付账款</CardTitle>
                <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
                  <TrendingDown className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summaryLoading ? '...' : formatCurrency(summary?.total_payable || 0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  逾期 {summary?.overdue_payable_count || 0} 笔
                </p>
              </CardContent>
            </Card>

            {/* 收款总额 */}
            <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push('/finance/payments')}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">本月收款</CardTitle>
                <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                  <ArrowUpRight className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summaryLoading ? '...' : formatCurrency(summary?.total_payment_in || 0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">较上月增长</p>
              </CardContent>
            </Card>

            {/* 付款总额 */}
            <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => router.push('/finance/payments')}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">本月付款</CardTitle>
                <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                  <ArrowDownRight className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {summaryLoading ? '...' : formatCurrency(summary?.total_payment_out || 0)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">较上月减少</p>
              </CardContent>
            </Card>
          </div>

          {/* 逾期预警 */}
          {summary && (summary.overdue_receivable_count > 0 || summary.overdue_payable_count > 0) && (
            <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-600 dark:text-red-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-red-900 dark:text-red-400 mb-2">逾期账款预警</h3>
                    <p className="text-sm text-red-700 dark:text-red-300 mb-4">
                      您有逾期的应收或应付账款需要及时处理
                    </p>
                    <div className="flex gap-4">
                      {summary.overdue_receivable_count > 0 && (
                        <Badge variant="destructive">逾期应收: {summary.overdue_receivable_count} 笔</Badge>
                      )}
                      {summary.overdue_payable_count > 0 && (
                        <Badge variant="destructive">逾期应付: {summary.overdue_payable_count} 笔</Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 快捷操作 */}
          <div>
            <h2 className="text-lg font-semibold mb-4">快捷操作</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button variant="outline" className="h-auto flex-col gap-3 py-4" onClick={() => router.push('/finance/receivables?action=create')}>
                <Plus className="h-6 w-6" />
                <div className="text-left">
                  <div className="font-medium">新建应收</div>
                  <div className="text-xs text-muted-foreground">创建客户应收账款</div>
                </div>
              </Button>
              <Button variant="outline" className="h-auto flex-col gap-3 py-4" onClick={() => router.push('/finance/payables?action=create')}>
                <Plus className="h-6 w-6" />
                <div className="text-left">
                  <div className="font-medium">新建应付</div>
                  <div className="text-xs text-muted-foreground">创建供应商应付账款</div>
                </div>
              </Button>
              <Button variant="outline" className="h-auto flex-col gap-3 py-4" onClick={() => router.push('/finance/payments?action=create&type=receipt')}>
                <Plus className="h-6 w-6" />
                <div className="text-left">
                  <div className="font-medium">收款单</div>
                  <div className="text-xs text-muted-foreground">记录客户收款</div>
                </div>
              </Button>
              <Button variant="outline" className="h-auto flex-col gap-3 py-4" onClick={() => router.push('/finance/accounts')}>
                <Settings className="h-6 w-6" />
                <div className="text-left">
                  <div className="font-medium">科目设置</div>
                  <div className="text-xs text-muted-foreground">管理会计科目</div>
                </div>
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
