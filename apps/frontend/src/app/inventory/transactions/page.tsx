/**
 * 库存流水页面
 * @description 查看库存出入库流水记录
 */

'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowDownToLine,
  ArrowUpFromLine,
  Filter,
  Calendar,
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
import type { InventoryTransaction } from '@/types/inventory';
import {
  TransactionType,
  TransactionTypeLabels,
  TransactionTypeColors,
} from '@/types/inventory';

// 流水类型分类
const inboundTypes: TransactionType[] = [
  TransactionType.PURCHASE_IN,
  TransactionType.SALES_RETURN,
  TransactionType.TRANSFER_IN,
  TransactionType.ADJUSTMENT_IN,
  TransactionType.OTHER_IN,
];

const outboundTypes: TransactionType[] = [
  TransactionType.PURCHASE_RETURN,
  TransactionType.SALES_OUT,
  TransactionType.TRANSFER_OUT,
  TransactionType.ADJUSTMENT_OUT,
  TransactionType.OTHER_OUT,
];

export default function TransactionsPage() {
  const [warehouseFilter, setWarehouseFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [directionFilter, setDirectionFilter] = useState<string>('all');

  // 获取仓库列表
  const { data: warehouses = [] } = useQuery({
    queryKey: ['inventory', 'warehouses'],
    queryFn: () => inventoryApi.warehouses.list(),
  });

  // 获取流水列表
  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['inventory', 'transactions', warehouseFilter, typeFilter, directionFilter],
    queryFn: () =>
      inventoryApi.inventories.transactions({
        warehouse_id: warehouseFilter === 'all' ? undefined : Number(warehouseFilter),
        transaction_type: typeFilter === 'all' ? undefined : (typeFilter as TransactionType),
      }),
  });

  // 根据出入库方向筛选
  const filteredTransactions = transactions.filter((t) => {
    if (directionFilter === 'all') return true;
    if (directionFilter === 'inbound') return inboundTypes.includes(t.transaction_type);
    if (directionFilter === 'outbound') return outboundTypes.includes(t.transaction_type);
    return true;
  });

  const columns: Column<InventoryTransaction>[] = [
    {
      id: 'transaction_type',
      header: '类型',
      cell: (row) => {
        const isInbound = inboundTypes.includes(row.transaction_type);
        return (
          <div className="flex items-center gap-1">
            {isInbound ? (
              <ArrowDownToLine className="h-4 w-4 text-green-500" />
            ) : (
              <ArrowUpFromLine className="h-4 w-4 text-red-500" />
            )}
            <Badge variant={TransactionTypeColors[row.transaction_type]}>
              {TransactionTypeLabels[row.transaction_type]}
            </Badge>
          </div>
        );
      },
      className: 'w-40',
    },
    {
      id: 'quantity',
      header: '数量',
      cell: (row) => {
        const isPositive = Number(row.quantity) > 0;
        return (
          <span
            className={`font-medium ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {isPositive ? '+' : ''}{row.quantity}
          </span>
        );
      },
      className: 'w-24',
    },
    {
      id: 'before_quantity',
      header: '变动前',
      cell: (row) => row.before_quantity?.toString() || '-',
      className: 'w-24',
    },
    {
      id: 'after_quantity',
      header: '变动后',
      cell: (row) => row.after_quantity?.toString() || '-',
      className: 'w-24',
    },
    {
      id: 'reference',
      header: '关联单据',
      cell: (row) =>
        row.reference_no ? (
          <div>
            <div className="text-sm">{row.reference_no}</div>
            {row.reference_type && (
              <div className="text-xs text-muted-foreground">{row.reference_type}</div>
            )}
          </div>
        ) : (
          '-'
        ),
      },
    {
      id: 'notes',
      header: '备注',
      cell: (row) => row.notes || '-',
    },
    {
      id: 'created_at',
      header: '时间',
      cell: (row) => (
        <div className="flex items-center gap-1">
          <Calendar className="h-3 w-3 text-muted-foreground" />
          {new Date(row.created_at).toLocaleString('zh-CN')}
        </div>
      ),
      className: 'w-40',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">库存流水</h1>
        <p className="text-muted-foreground mt-1">
          查看所有库存出入库记录
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              总记录数
            </CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredTransactions.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              入库记录
            </CardTitle>
            <ArrowDownToLine className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {filteredTransactions.filter((t) =>
                inboundTypes.includes(t.transaction_type)
              ).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              出库记录
            </CardTitle>
            <ArrowUpFromLine className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {filteredTransactions.filter((t) =>
                outboundTypes.includes(t.transaction_type)
              ).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 流水列表 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>流水记录</CardTitle>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <Select
                value={directionFilter}
                onValueChange={(value) => {
                  setDirectionFilter(value);
                  setTypeFilter('all');
                }}
              >
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="出入库" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="inbound">入库</SelectItem>
                  <SelectItem value="outbound">出库</SelectItem>
                </SelectContent>
              </Select>
              <Select value={warehouseFilter} onValueChange={setWarehouseFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="仓库" />
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
              <Select
                value={typeFilter}
                onValueChange={(value) => {
                  setTypeFilter(value);
                  setDirectionFilter('all');
                }}
              >
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="流水类型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部类型</SelectItem>
                  {Object.entries(TransactionTypeLabels).map(([value, label]) => (
                    <SelectItem key={value} value={value}>
                      {label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable
            data={filteredTransactions}
            columns={columns}
            isLoading={isLoading}
            pagination
            pageSize={20}
            emptyMessage="暂无流水记录"
          />
        </CardContent>
      </Card>

      {/* 图例说明 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">流水类型说明</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="font-medium text-green-600 mb-1">入库类型</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• 采购入库</li>
                <li>• 销售退货</li>
                <li>• 调拨入库</li>
                <li>• 盘盈</li>
                <li>• 其他入库</li>
              </ul>
            </div>
            <div>
              <div className="font-medium text-red-600 mb-1">出库类型</div>
              <ul className="space-y-1 text-muted-foreground">
                <li>• 采购退货</li>
                <li>• 销售出库</li>
                <li>• 调拨出库</li>
                <li>• 盘亏</li>
                <li>• 其他出库</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
