/**
 * 产品管理页面
 * @description 管理产品信息，包括创建、编辑、删除产品
 */

'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
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
import type { Product } from '@/types/inventory';
import { ProductStatus, ProductStatusLabels, ProductStatusColors } from '@/types/inventory';

export default function ProductsPage() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    specification: '',
    unit: '',
    category: '',
    barcode: '',
    cost_price: '',
    selling_price: '',
    min_stock: '',
    max_stock: '',
    lead_time: '',
    notes: '',
    status: ProductStatus.ACTIVE,
  });

  // 获取产品列表
  const { data: products = [], isLoading } = useQuery({
    queryKey: ['inventory', 'products', searchTerm, statusFilter],
    queryFn: () =>
      inventoryApi.products.list({
        keyword: searchTerm || undefined,
        status: statusFilter === 'all' ? undefined : statusFilter,
      }),
  });

  // 创建产品
  const createMutation = useMutation({
    mutationFn: inventoryApi.products.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'products'] });
      setIsCreateDialogOpen(false);
      resetForm();
    },
  });

  // 更新产品
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      inventoryApi.products.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'products'] });
      setIsEditDialogOpen(false);
      setSelectedProduct(null);
      resetForm();
    },
  });

  // 删除产品
  const deleteMutation = useMutation({
    mutationFn: inventoryApi.products.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'products'] });
      setIsDeleteDialogOpen(false);
      setSelectedProduct(null);
    },
  });

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      specification: '',
      unit: '',
      category: '',
      barcode: '',
      cost_price: '',
      selling_price: '',
      min_stock: '',
      max_stock: '',
      lead_time: '',
      notes: '',
      status: ProductStatus.ACTIVE,
    });
  };

  const handleCreate = () => {
    createMutation.mutate({
      ...formData,
      cost_price: formData.cost_price ? Number(formData.cost_price) : undefined,
      selling_price: formData.selling_price ? Number(formData.selling_price) : undefined,
      min_stock: formData.min_stock ? Number(formData.min_stock) : undefined,
      max_stock: formData.max_stock ? Number(formData.max_stock) : undefined,
      lead_time: formData.lead_time ? Number(formData.lead_time) : undefined,
    });
  };

  const handleEdit = () => {
    if (!selectedProduct) return;
    updateMutation.mutate({
      id: selectedProduct.id,
      data: {
        ...formData,
        cost_price: formData.cost_price ? Number(formData.cost_price) : undefined,
        selling_price: formData.selling_price ? Number(formData.selling_price) : undefined,
        min_stock: formData.min_stock ? Number(formData.min_stock) : undefined,
        max_stock: formData.max_stock ? Number(formData.max_stock) : undefined,
        lead_time: formData.lead_time ? Number(formData.lead_time) : undefined,
      },
    });
  };

  const handleDelete = () => {
    if (!selectedProduct) return;
    deleteMutation.mutate(selectedProduct.id);
  };

  const openEditDialog = (product: Product) => {
    setSelectedProduct(product);
    setFormData({
      code: product.code,
      name: product.name,
      specification: product.specification || '',
      unit: product.unit || '',
      category: product.category || '',
      barcode: product.barcode || '',
      cost_price: product.cost_price?.toString() || '',
      selling_price: product.selling_price?.toString() || '',
      min_stock: product.min_stock?.toString() || '',
      max_stock: product.max_stock?.toString() || '',
      lead_time: product.lead_time?.toString() || '',
      notes: product.notes || '',
      status: product.status,
    });
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (product: Product) => {
    setSelectedProduct(product);
    setIsDeleteDialogOpen(true);
  };

  const columns: Column<Product>[] = [
    {
      id: 'code',
      header: '产品编码',
      cell: (row) => <span className="font-medium">{row.code}</span>,
      sortable: true,
    },
    {
      id: 'name',
      header: '产品名称',
      cell: (row) => row.name,
      sortable: true,
    },
    {
      id: 'specification',
      header: '规格型号',
      cell: (row) => row.specification || '-',
    },
    {
      id: 'unit',
      header: '单位',
      cell: (row) => row.unit || '-',
      className: 'w-20',
    },
    {
      id: 'category',
      header: '分类',
      cell: (row) => row.category || '-',
    },
    {
      id: 'cost_price',
      header: '成本价',
      cell: (row) => (row.cost_price ? `¥${row.cost_price}` : '-'),
      className: 'w-24',
    },
    {
      id: 'selling_price',
      header: '销售价',
      cell: (row) => (row.selling_price ? `¥${row.selling_price}` : '-'),
      className: 'w-24',
    },
    {
      id: 'status',
      header: '状态',
      cell: (row) => (
        <Badge variant={ProductStatusColors[row.status] as any}>
          {ProductStatusLabels[row.status]}
        </Badge>
      ),
      className: 'w-24',
    },
    {
      id: 'actions',
      header: '操作',
      cell: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation();
              openEditDialog(row);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
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
        </div>
      ),
      className: 'w-24',
    },
  ];

  const ProductForm = () => (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="code">产品编码 *</Label>
        <Input
          id="code"
          value={formData.code}
          onChange={(e) => setFormData({ ...formData, code: e.target.value })}
          disabled={!!selectedProduct}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="name">产品名称 *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="specification">规格型号</Label>
        <Input
          id="specification"
          value={formData.specification}
          onChange={(e) => setFormData({ ...formData, specification: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="unit">单位</Label>
        <Input
          id="unit"
          value={formData.unit}
          onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
          placeholder="如：件、个、箱"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="category">分类</Label>
        <Input
          id="category"
          value={formData.category}
          onChange={(e) => setFormData({ ...formData, category: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="barcode">条码</Label>
        <Input
          id="barcode"
          value={formData.barcode}
          onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="cost_price">成本价</Label>
        <Input
          id="cost_price"
          type="number"
          step="0.01"
          value={formData.cost_price}
          onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="selling_price">销售价</Label>
        <Input
          id="selling_price"
          type="number"
          step="0.01"
          value={formData.selling_price}
          onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="min_stock">最小库存</Label>
        <Input
          id="min_stock"
          type="number"
          step="0.01"
          value={formData.min_stock}
          onChange={(e) => setFormData({ ...formData, min_stock: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="max_stock">最大库存</Label>
        <Input
          id="max_stock"
          type="number"
          step="0.01"
          value={formData.max_stock}
          onChange={(e) => setFormData({ ...formData, max_stock: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="lead_time">采购提前期（天）</Label>
        <Input
          id="lead_time"
          type="number"
          value={formData.lead_time}
          onChange={(e) => setFormData({ ...formData, lead_time: e.target.value })}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="status">状态</Label>
        <Select
          value={formData.status}
          onValueChange={(value) => setFormData({ ...formData, status: value as ProductStatus })}
        >
          <SelectTrigger id="status">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(ProductStatusLabels).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2 col-span-2">
        <Label htmlFor="notes">备注</Label>
        <Input
          id="notes"
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
        />
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">产品管理</h1>
          <p className="text-muted-foreground mt-1">
            管理产品信息、价格和库存预警设置
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          新建产品
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <DataTable
            data={products}
            columns={columns}
            isLoading={isLoading}
            searchable
            searchableFields={['code', 'name', 'category']}
            emptyMessage="暂无产品数据"
          />
        </CardContent>
      </Card>

      {/* 创建产品对话框 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl" onClose={() => setIsCreateDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>新建产品</DialogTitle>
            <DialogDescription>
              填写产品信息，带 * 的为必填项
            </DialogDescription>
          </DialogHeader>
          <ProductForm />
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

      {/* 编辑产品对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl" onClose={() => setIsEditDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>编辑产品</DialogTitle>
            <DialogDescription>
              修改产品信息
            </DialogDescription>
          </DialogHeader>
          <ProductForm />
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleEdit} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? '保存中...' : '保存'}
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
              确定要删除产品「{selectedProduct?.name}」吗？此操作不可撤销。
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
