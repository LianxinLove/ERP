/**
 * 库存调拨页面
 * @description 管理仓库间的库存调拨
 */

'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, ArrowRight, Play, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { DataTable, Column } from '@/components/data-table/DataTable';
import { inventoryApi } from '@/api/inventory';
import type { InventoryTransfer, Product, Warehouse } from '@/types/inventory';
import {
  TransferStatus,
  TransferStatusLabels,
  TransferStatusColors,
} from '@/types/inventory';

interface TransferItem {
  product_id: string;
  quantity: string;
  notes?: string;
}

interface TransferFormProps {
  formData: {
    from_warehouse_id: string;
    to_warehouse_id: string;
    transfer_date: string;
    notes: string;
    items: TransferItem[];
  };
  warehouses: Warehouse[];
  products: Product[];
  onChange: (data: any) => void;
  onAddItem: () => void;
  onRemoveItem: (index: number) => void;
  onUpdateItem: (index: number, field: string, value: string) => void;
}

const TransferForm = React.memo(function TransferForm({
  formData,
  warehouses,
  products,
  onChange,
  onAddItem,
  onRemoveItem,
  onUpdateItem,
}: TransferFormProps) {
  const handleChange = (field: string, value: string) => {
    onChange({ ...formData, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="from_warehouse">调出仓库 *</Label>
          <Select
            value={formData.from_warehouse_id}
            onValueChange={(value) => handleChange('from_warehouse_id', value)}
          >
            <SelectTrigger id="from_warehouse">
              <SelectValue placeholder="选择调出仓库" />
            </SelectTrigger>
            <SelectContent>
              {warehouses.map((wh) => (
                <SelectItem key={wh.id} value={wh.id.toString()}>
                  {wh.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="to_warehouse">调入仓库 *</Label>
          <Select
            value={formData.to_warehouse_id}
            onValueChange={(value) => handleChange('to_warehouse_id', value)}
          >
            <SelectTrigger id="to_warehouse">
              <SelectValue placeholder="选择调入仓库" />
            </SelectTrigger>
            <SelectContent>
              {warehouses.map((wh) => (
                <SelectItem key={wh.id} value={wh.id.toString()}>
                  {wh.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="transfer_date">调拨日期 *</Label>
        <Input
          id="transfer_date"
          type="date"
          value={formData.transfer_date}
          onChange={(e) => handleChange('transfer_date', e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label>调拨明细 *</Label>
          <Button type="button" variant="outline" size="sm" onClick={onAddItem}>
            <Plus className="h-4 w-4 mr-1" />
            添加明细
          </Button>
        </div>
        {formData.items.length === 0 ? (
          <div className="text-center py-4 text-muted-foreground text-sm border rounded-md">
            暂无明细，请点击"添加明细"添加
          </div>
        ) : (
          <div className="space-y-2 border rounded-md p-3">
            {formData.items.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <Select
                  value={item.product_id}
                  onValueChange={(value) => onUpdateItem(index, 'product_id', value)}
                >
                  <SelectTrigger className="flex-1">
                    <SelectValue placeholder="选择产品" />
                  </SelectTrigger>
                  <SelectContent>
                    {products.map((p) => (
                      <SelectItem key={p.id} value={p.id.toString()}>
                        {p.code} - {p.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Input
                  type="number"
                  step="0.01"
                  placeholder="数量"
                  value={item.quantity}
                  onChange={(e) => onUpdateItem(index, 'quantity', e.target.value)}
                  className="w-24"
                />
                <Input
                  placeholder="备注"
                  value={item.notes || ''}
                  onChange={(e) => onUpdateItem(index, 'notes', e.target.value)}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => onRemoveItem(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="notes">备注</Label>
        <Input
          id="notes"
          value={formData.notes}
          onChange={(e) => handleChange('notes', e.target.value)}
          placeholder="请输入备注信息"
        />
      </div>
    </div>
  );
});

export default function TransfersPage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedTransfer, setSelectedTransfer] = useState<InventoryTransfer | null>(null);
  const [formData, setFormData] = useState({
    from_warehouse_id: '',
    to_warehouse_id: '',
    transfer_date: new Date().toISOString().split('T')[0],
    notes: '',
    items: [] as Array<{ product_id: string; quantity: string; notes?: string }>,
  });

  // 获取仓库列表
  const { data: warehouses = [] } = useQuery({
    queryKey: ['inventory', 'warehouses'],
    queryFn: () => inventoryApi.warehouses.list(),
  });

  // 获取产品列表
  const { data: products = [] } = useQuery({
    queryKey: ['inventory', 'products'],
    queryFn: () => inventoryApi.products.list(),
  });

  // 获取调拨单列表
  const { data: transfers = [], isLoading } = useQuery({
    queryKey: ['inventory', 'transfers', statusFilter],
    queryFn: () =>
      inventoryApi.transfers.list({
        status: statusFilter === 'all' ? undefined : (statusFilter as any),
      }),
  });

  // 创建调拨单
  const createMutation = useMutation({
    mutationFn: inventoryApi.transfers.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'transfers'] });
      setIsCreateDialogOpen(false);
      resetForm();
    },
  });

  // 执行调拨
  const executeMutation = useMutation({
    mutationFn: inventoryApi.transfers.execute,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'transfers'] });
    },
  });

  // 删除调拨单
  const deleteMutation = useMutation({
    mutationFn: inventoryApi.transfers.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'transfers'] });
      setIsDeleteDialogOpen(false);
      setSelectedTransfer(null);
    },
  });

  const resetForm = () => {
    setFormData({
      from_warehouse_id: '',
      to_warehouse_id: '',
      transfer_date: new Date().toISOString().split('T')[0],
      notes: '',
      items: [],
    });
  };

  const handleCreate = () => {
    const validItems = formData.items.filter(
      (item) => item.product_id && item.quantity && Number(item.quantity) > 0
    );

    if (validItems.length === 0) {
      alert('请至少添加一个有效的调拨明细');
      return;
    }

    if (formData.from_warehouse_id === formData.to_warehouse_id) {
      alert('调出仓库和调入仓库不能相同');
      return;
    }

    createMutation.mutate({
      from_warehouse_id: Number(formData.from_warehouse_id),
      to_warehouse_id: Number(formData.to_warehouse_id),
      transfer_date: new Date(formData.transfer_date).toISOString(),
      notes: formData.notes || undefined,
      items: validItems.map((item) => ({
        product_id: Number(item.product_id),
        quantity: Number(item.quantity),
        notes: item.notes,
      })),
    });
  };

  const handleExecute = (transferId: number) => {
    if (confirm('确定要执行此调拨单吗？执行后库存将会发生变化。')) {
      executeMutation.mutate(transferId);
    }
  };

  const handleDelete = () => {
    if (!selectedTransfer) return;
    deleteMutation.mutate(selectedTransfer.id);
  };

  const openDeleteDialog = (transfer: InventoryTransfer) => {
    setSelectedTransfer(transfer);
    setIsDeleteDialogOpen(true);
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { product_id: '', quantity: '', notes: '' }],
    });
  };

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index),
    });
  };

  const updateItem = (index: number, field: string, value: string) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData({ ...formData, items: newItems });
  };

  const columns: Column<InventoryTransfer>[] = [
    {
      id: 'transfer_no',
      header: '调拨单号',
      cell: (row) => <span className="font-medium">{row.transfer_no}</span>,
      sortable: true,
    },
    {
      id: 'from_to',
      header: '调拨路径',
      cell: (row) => {
        const fromWh = warehouses.find((w) => w.id === row.from_warehouse_id);
        const toWh = warehouses.find((w) => w.id === row.to_warehouse_id);
        return (
          <div className="flex items-center gap-1">
            <span className="text-sm">{fromWh?.name || row.from_warehouse_id}</span>
            <ArrowRight className="h-3 w-3 text-muted-foreground" />
            <span className="text-sm">{toWh?.name || row.to_warehouse_id}</span>
          </div>
        );
      },
    },
    {
      id: 'transfer_date',
      header: '调拨日期',
      cell: (row) => new Date(row.transfer_date).toLocaleDateString('zh-CN'),
      className: 'w-32',
    },
    {
      id: 'status',
      header: '状态',
      cell: (row) => (
        <Badge variant={TransferStatusColors[row.status] as any}>
          {TransferStatusLabels[row.status]}
        </Badge>
      ),
      className: 'w-28',
    },
    {
      id: 'actions',
      header: '操作',
      cell: (row) => (
        <div className="flex items-center gap-2">
          {row.status === TransferStatus.DRAFT && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleExecute(row.id)}
              disabled={executeMutation.isPending}
            >
              <Play className="h-3 w-3 mr-1" />
              执行
            </Button>
          )}
          {row.status === TransferStatus.DRAFT && (
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                openDeleteDialog(row);
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
      className: 'w-32',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">库存调拨</h1>
          <p className="text-muted-foreground mt-1">
            管理仓库间的库存调拨
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          新建调拨单
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>调拨单列表</CardTitle>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="状态筛选" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                {Object.entries(TransferStatusLabels).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable
            data={transfers}
            columns={columns}
            isLoading={isLoading}
            searchable
            searchableFields={['transfer_no']}
            emptyMessage="暂无调拨单"
          />
        </CardContent>
      </Card>

      {/* 创建调拨单对话框 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto" onClose={() => setIsCreateDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>新建调拨单</DialogTitle>
            <DialogDescription>
              创建仓库间库存调拨单，填写调拨信息和明细
            </DialogDescription>
          </DialogHeader>
          <TransferForm
            formData={formData}
            warehouses={warehouses}
            products={products}
            onChange={setFormData}
            onAddItem={addItem}
            onRemoveItem={removeItem}
            onUpdateItem={updateItem}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleCreate} disabled={createMutation.isPending}>
              {createMutation.isPending ? '创建中...' : '创建'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认对话框 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent onClose={() => setIsDeleteDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除调拨单「{selectedTransfer?.transfer_no}」吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? '删除中...' : '删除'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
