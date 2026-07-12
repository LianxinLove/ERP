/**
 * 采购管理主页
 */

'use client';

import Link from 'next/link';
import { Package, ShoppingCart, Users } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function PurchasePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">采购管理</h1>
        <p className="text-muted-foreground mt-1">
          管理供应商、采购申请和采购订单
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/purchase/suppliers">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <CardTitle>供应商管理</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">管理供应商信息、联系方式和合作状态</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/purchase/requests">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                  <ShoppingCart className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <CardTitle>采购申请</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">创建和管理采购申请，发起审批流程</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/purchase/orders">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                  <Package className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <CardTitle>采购订单</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">管理采购订单，跟踪订单状态和交付</p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
