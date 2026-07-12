/**
 * 销售订单页面
 */

'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function SalesOrdersPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">销售订单</h1>
          <p className="text-muted-foreground mt-1">
            管理和跟踪所有销售订单
          </p>
        </div>
        <Button>创建订单</Button>
      </div>

      <Card>
        <CardContent className="p-12">
          <p className="text-muted-foreground text-center">
            销售订单列表将在这里显示
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
