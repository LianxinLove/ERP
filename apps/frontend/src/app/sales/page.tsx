/**
 * 销售管理主页
 */

'use client';

import Link from 'next/link';
import { Users, ShoppingCart, Undo2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function SalesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">销售管理</h1>
        <p className="text-muted-foreground mt-1">
          管理客户、销售订单和销售退货
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/sales/customers">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <CardTitle>客户管理</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">管理客户信息、联系记录和信用状态</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/sales/orders">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                  <ShoppingCart className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <CardTitle>销售订单</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">创建和管理销售订单，跟踪订单状态</p>
            </CardContent>
          </Card>
        </Link>

        <Link href="/sales/returns">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                  <Undo2 className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                </div>
                <CardTitle>销售退货</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">处理客户退货请求，管理退款流程</p>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
