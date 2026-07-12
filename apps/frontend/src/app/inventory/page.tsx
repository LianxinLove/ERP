/**
 * 库存管理主页
 * @description 库存总览，包含统计卡片和库存列表
 */

'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  Package,
  Building,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  Filter,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DataTable, Column } from '@/components/data-table/DataTable';
import { inventoryApi } from '@/api/inventory';
import type { InventoryDetail } from '@/types/inventory';
import { formatCurrency } from '@/lib/utils';

export default function InventoryPage() {
  const [warehouseFilter, setWarehouseFilter] = useState<string>('all');
  const [lowStockOnly, setLowStockOnly] = useState(false);

  // 获取仓库列表
  const { data: warehouses = [] } = useQuery({
    queryKey: ['inventory', 'warehouses'],
    queryFn: () => inventoryApi.warehouses.list(),
  });

  // 获取库存列表
  const { data: inventories = [], isLoading } = useQuery({
    queryKey: ['inventory', 'inventories', warehouseFilter, lowStockOnly],
    queryFn: () =>
      inventoryApi.inventories.list({
        warehouse_id: warehouseFilter === 'all' ? undefined : Number(warehouseFilter),
        low_stock_only: lowStockOnly || undefined,
      }),
  });

  // 计算统计数据
  const stats = {
    totalProducts: new Set(inventories.map((i) => i.product_id)).size,
    totalWarehouses: warehouses.length,
    totalItems: inventories.reduce((sum, i) => sum + Number(i.quantity), 0),
    lowStockCount: inventories.filter(
      (i) => Number(i.available_quantity) <= 0
    ).length,
  };

  const columns: Column<InventoryDetail>[] = [
    {
      id: 'product_code',
      header: '产品编码',
      cell: (row) => (
        <div>
          <div className="font-medium">{row.product_code || '-'}</div>
          <div className="text-sm text-muted-foreground">{row.product_name || '-'}</div>
        </div>
      ),
      sortable: true,
    },
    {
      id: 'warehouse_name',
      header: '仓库',
      cell: (row) => (
        <div className="flex items-center gap-1">
          <Building className="h-3 w-3 text-muted-foreground" />
          {row.warehouse_name || '-'}
        </div>
      ),
    },
    {
      id: 'quantity',
      header: '库存数量',
      cell: (row) => (
        <div>
          <div className="font-medium">{row.quantity}</div>
          <div className="text-sm text-muted-foreground">可用: {row.available_quantity}</div>
        </div>
      ),
      sortable: true,
      className: 'w-32',
    },
    {
      id: 'allocated_quantity',
      header: '已分配',
      cell: (row) => (
        <span className="text-muted-foreground">{row.allocated_quantity}</span>
      ),
      className: 'w-24',
    },
    {
      id: 'available_quantity',
      header: '可用数量',
      cell: (row) => {
        const available = Number(row.available_quantity);
        const isLow = available <= 0;
        return (
          <Badge variant={isLow ? 'destructive' : 'default'}>
            {available}
          </Badge>
        );
      },
      sortable: true,
      className: 'w-28',
    },
    {
      id: 'last_updated',
      header: '最后更新',
      cell: (row) =>
        row.last_updated
          ? new Date(row.last_updated).toLocaleDateString('zh-CN')
          : '-',
      className: 'w-32',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">库存管理</h1>
        <p className="text-muted-foreground mt-1">
          查看和管理库存、出入库记录和库存预警
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              产品总数
            </CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProducts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              仓库数量
            </CardTitle>
            <Building className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalWarehouses}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              库存总量
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalItems.toLocaleString()}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              低库存预警
            </CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-500">
              {stats.lowStockCount}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 快捷入口 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Link href="/inventory/products">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <div className="font-medium">产品管理</div>
                <div className="text-sm text-muted-foreground">
                  管理产品信息
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>

        <Link href="/inventory/warehouses">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <div className="font-medium">仓库管理</div>
                <div className="text-sm text-muted-foreground">
                  管理仓库信息
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>

        <Link href="/inventory/transactions">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <div className="font-medium">库存流水</div>
                <div className="text-sm text-muted-foreground">
                  查看出入库记录
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>

        <Link href="/inventory/transfers">
          <Card className="hover:bg-muted/50 transition-colors cursor-pointer">
            <CardContent className="flex items-center justify-between p-4">
              <div>
                <div className="font-medium">库存调拨</div>
                <div className="text-sm text-muted-foreground">
                  仓库间调拨
                </div>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground" />
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* 库存列表 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>库存列表</CardTitle>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <Select value={warehouseFilter} onValueChange={setWarehouseFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="选择仓库" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部仓库</SelectItem>
                  {warehouses.map((wh) => (
                    <SelectItem key={wh.id} value={wh.id.toString()}>
                      {wh.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant={lowStockOnly ? 'default' : 'outline'}
                size="sm"
                onClick={() => setLowStockOnly(!lowStockOnly)}
              >
                <AlertTriangle className="h-4 w-4 mr-1" />
                仅低库存
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable
            data={inventories}
            columns={columns}
            isLoading={isLoading}
            searchable
            searchableFields={['product_code', 'product_name', 'warehouse_name']}
            emptyMessage="暂无库存数据"
          />
        </CardContent>
      </Card>
    </div>
  );
}
