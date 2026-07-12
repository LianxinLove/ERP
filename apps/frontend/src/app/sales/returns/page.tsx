/**
 * 销售退货页面
 */

'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function SalesReturnsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">销售退货</h1>
          <p className="text-muted-foreground mt-1">
            管理客户退货和退款流程
          </p>
        </div>
        <Button>创建退货单</Button>
      </div>

      <Card>
        <CardContent className="p-12">
          <p className="text-muted-foreground text-center">
            销售退货列表将在这里显示
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
