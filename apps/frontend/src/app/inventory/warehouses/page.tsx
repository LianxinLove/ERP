/**
 * 仓库管理页面
 * @description 管理仓库信息，包括创建、编辑、删除仓库
 */

'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2, MapPin, Phone, User } from 'lucide-react';
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
import { DataTable, Column } from '@/components/data-table/DataTable';
import { inventoryApi } from '@/api/inventory';
import type { Warehouse } from '@/types/inventory';

interface WarehouseFormProps {
  formData: {
    code: string;
    name: string;
    address: string;
    manager_id: string;
    contact: string;
    capacity: string;
    notes: string;
  };
  onChange: (data: any) => void;
  isEdit?: boolean;
}

const WarehouseForm = React.memo(function WarehouseForm({ formData, onChange, isEdit = false }: WarehouseFormProps) {
  const handleChange = (field: string, value: string) => {
    onChange({ ...formData, [field]: value });
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="code">仓库编码 *</Label>
        <Input
          id="code"
          value={formData.code}
          onChange={(e) => handleChange('code', e.target.value)}
          disabled={isEdit}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="name">仓库名称 *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
        />
      </div>
      <div className="space-y-2 col-span-2">
        <Label htmlFor="address">地址</Label>
        <Input
          id="address"
          value={formData.address}
          onChange={(e) => handleChange('address', e.target.value)}
          placeholder="请输入仓库地址"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="contact">联系电话</Label>
        <Input
          id="contact"
          value={formData.contact}
          onChange={(e) => handleChange('contact', e.target.value)}
          placeholder="请输入联系电话"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="manager_id">负责人ID</Label>
        <Input
          id="manager_id"
          type="number"
          value={formData.manager_id}
          onChange={(e) => handleChange('manager_id', e.target.value)}
          placeholder="请输入负责人用户ID"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="capacity">容量（m³）</Label>
        <Input
          id="capacity"
          type="number"
          step="0.01"
          value={formData.capacity}
          onChange={(e) => handleChange('capacity', e.target.value)}
          placeholder="请输入仓库容量"
        />
      </div>
      <div className="space-y-2 col-span-2">
        <Label htmlFor="notes">备注</Label>
        <Input
          id="notes"
          value={formData.notes}
          onChange={(e) => handleChange('notes', e.target.value)}
        />
      </div>
    </div>
  );
});

export default function WarehousesPage() {
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    address: '',
    manager_id: '',
    contact: '',
    capacity: '',
    notes: '',
  });

  // 获取仓库列表
  const { data: warehouses = [], isLoading } = useQuery({
    queryKey: ['inventory', 'warehouses'],
    queryFn: () => inventoryApi.warehouses.list(),
  });

  // 创建仓库
  const createMutation = useMutation({
    mutationFn: inventoryApi.warehouses.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'warehouses'] });
      setIsCreateDialogOpen(false);
      resetForm();
    },
  });

  // 更新仓库
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      inventoryApi.warehouses.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'warehouses'] });
      setIsEditDialogOpen(false);
      setSelectedWarehouse(null);
      resetForm();
    },
  });

  // 删除仓库
  const deleteMutation = useMutation({
    mutationFn: inventoryApi.warehouses.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory', 'warehouses'] });
      setIsDeleteDialogOpen(false);
      setSelectedWarehouse(null);
    },
  });

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      address: '',
      manager_id: '',
      contact: '',
      capacity: '',
      notes: '',
    });
  };

  const handleCreate = () => {
    createMutation.mutate({
      ...formData,
      manager_id: formData.manager_id ? Number(formData.manager_id) : undefined,
      capacity: formData.capacity ? Number(formData.capacity) : undefined,
    });
  };

  const handleEdit = () => {
    if (!selectedWarehouse) return;
    updateMutation.mutate({
      id: selectedWarehouse.id,
      data: {
        ...formData,
        manager_id: formData.manager_id ? Number(formData.manager_id) : undefined,
        capacity: formData.capacity ? Number(formData.capacity) : undefined,
      },
    });
  };

  const handleDelete = () => {
    if (!selectedWarehouse) return;
    deleteMutation.mutate(selectedWarehouse.id);
  };

  const openEditDialog = (warehouse: Warehouse) => {
    setSelectedWarehouse(warehouse);
    setFormData({
      code: warehouse.code,
      name: warehouse.name,
      address: warehouse.address || '',
      manager_id: warehouse.manager_id?.toString() || '',
      contact: warehouse.contact || '',
      capacity: warehouse.capacity?.toString() || '',
      notes: warehouse.notes || '',
    });
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (warehouse: Warehouse) => {
    setSelectedWarehouse(warehouse);
    setIsDeleteDialogOpen(true);
  };

  const columns: Column<Warehouse>[] = [
    {
      id: 'code',
      header: '仓库编码',
      cell: (row) => <span className="font-medium">{row.code}</span>,
      sortable: true,
    },
    {
      id: 'name',
      header: '仓库名称',
      cell: (row) => row.name,
      sortable: true,
    },
    {
      id: 'address',
      header: '地址',
      cell: (row) =>
        row.address ? (
          <div className="flex items-center gap-1 text-muted-foreground">
            <MapPin className="h-3 w-3" />
            <span className="truncate max-w-[200px]">{row.address}</span>
          </div>
        ) : (
          '-'
        ),
    },
    {
      id: 'contact',
      header: '联系电话',
      cell: (row) =>
        row.contact ? (
          <div className="flex items-center gap-1">
            <Phone className="h-3 w-3 text-muted-foreground" />
            {row.contact}
          </div>
        ) : (
          '-'
        ),
    },
    {
      id: 'manager_id',
      header: '负责人ID',
      cell: (row) =>
        row.manager_id ? (
          <div className="flex items-center gap-1">
            <User className="h-3 w-3 text-muted-foreground" />
            {row.manager_id}
          </div>
        ) : (
          '-'
        ),
    },
    {
      id: 'capacity',
      header: '容量',
      cell: (row) => (row.capacity ? `${row.capacity} m³` : '-'),
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">仓库管理</h1>
          <p className="text-muted-foreground mt-1">
            管理仓库信息、地址和容量设置
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          新建仓库
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <DataTable
            data={warehouses}
            columns={columns}
            isLoading={isLoading}
            searchable
            searchableFields={['code', 'name', 'address']}
            emptyMessage="暂无仓库数据"
          />
        </CardContent>
      </Card>

      {/* 创建仓库对话框 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="max-w-2xl" onClose={() => setIsCreateDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>新建仓库</DialogTitle>
            <DialogDescription>
              填写仓库信息，带 * 的为必填项
            </DialogDescription>
          </DialogHeader>
          <WarehouseForm
            formData={formData}
            onChange={setFormData}
            isEdit={false}
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

      {/* 编辑仓库对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl" onClose={() => setIsEditDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>编辑仓库</DialogTitle>
            <DialogDescription>
              修改仓库信息
            </DialogDescription>
          </DialogHeader>
          <WarehouseForm
            formData={formData}
            onChange={setFormData}
            isEdit={true}
          />
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
              确定要删除仓库「{selectedWarehouse?.name}」吗？此操作不可撤销。
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
