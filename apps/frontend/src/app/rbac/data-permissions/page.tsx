/**
 * 数据权限配置页面
 * @description 配置用户的数据访问范围
 */

"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { dataPermissionApi } from '@/api/rbac';
import type { DataPermission, DataPermissionCreate, DataScope } from '@/types/rbac';
import { Plus, Edit, Trash2, Shield, Database } from 'lucide-react';
import { toast } from 'sonner';

// 数据范围选项
const dataScopeOptions: Array<{ value: DataScope; label: string; description: string }> = [
  { value: 'all', label: '全部数据', description: '可以访问所有数据' },
  { value: 'department', label: '本部门', description: '只能访问本部门的数据' },
  { value: 'self', label: '本人', description: '只能访问自己的数据' },
  { value: 'custom', label: '自定义', description: '自定义访问范围' },
];

// 资源类型选项
const resourceTypeOptions = [
  { value: 'sales_order', label: '销售订单' },
  { value: 'purchase_order', label: '采购订单' },
  { value: 'inventory', label: '库存' },
  { value: 'finance', label: '财务' },
  { value: 'customer', label: '客户' },
  { value: 'supplier', label: '供应商' },
];

export default function DataPermissionsPage() {
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [editingPermission, setEditingPermission] = useState<DataPermission | null>(null);
  const [selectedResourceType, setSelectedResourceType] = useState<string>('all');

  // 创建表单状态
  const [createForm, setCreateForm] = useState<DataPermissionCreate>({
    user_id: 0,
    resource_type: 'sales_order',
    scope: 'self',
  });

  // 编辑表单状态
  const [editForm, setEditForm] = useState<Partial<DataPermissionCreate>>({
    scope: 'self',
  });

  // 获取数据权限列表
  const { data: dataPermissions, isLoading } = useQuery({
    queryKey: ['data-permissions', selectedResourceType],
    queryFn: () =>
      selectedResourceType === 'all'
        ? Promise.resolve([]) // 实际应调用获取所有数据的API
        : dataPermissionApi.getByResourceType(selectedResourceType),
    enabled: false, // 暂时禁用，等待后端API实现
  });

  // 创建数据权限
  const createMutation = useMutation({
    mutationFn: (data: DataPermissionCreate) => dataPermissionApi.createPermission(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-permissions'] });
      setIsCreateDialogOpen(false);
      toast.success('数据权限创建成功');
      resetCreateForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '创建失败');
    },
  });

  // 更新数据权限
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<DataPermissionCreate> }) =>
      dataPermissionApi.updatePermission(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-permissions'] });
      setIsEditDialogOpen(false);
      toast.success('数据权限更新成功');
      setEditingPermission(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '更新失败');
    },
  });

  // 删除数据权限
  const deleteMutation = useMutation({
    mutationFn: (id: number) => dataPermissionApi.deletePermission(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-permissions'] });
      setDeleteId(null);
      toast.success('数据权限删除成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '删除失败');
    },
  });

  const resetCreateForm = () => {
    setCreateForm({
      user_id: 0,
      resource_type: 'sales_order',
      scope: 'self',
    });
  };

  const handleCreate = () => {
    if (!createForm.user_id) {
      toast.error('请输入用户ID');
      return;
    }

    createMutation.mutate(createForm);
  };

  const handleEdit = (permission: DataPermission) => {
    setEditingPermission(permission);
    setEditForm({
      resource_type: permission.resource_type,
      scope: permission.scope,
      department_ids: permission.department_ids,
      user_ids: permission.user_ids,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!editingPermission) return;

    updateMutation.mutate({
      id: editingPermission.id,
      data: editForm,
    });
  };

  const confirmDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId);
    }
  };

  const getScopeLabel = (scope: DataScope) => {
    return dataScopeOptions.find((opt) => opt.value === scope)?.label || scope;
  };

  const getResourceTypeLabel = (resourceType: string) => {
    return resourceTypeOptions.find((opt) => opt.value === resourceType)?.label || resourceType;
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">数据权限配置</h1>
          <p className="text-muted-foreground mt-1">
            配置用户的数据访问范围
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新建配置
            </Button>
          </DialogTrigger>
          <DialogContent onClose={() => setIsCreateDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>新建数据权限</DialogTitle>
              <DialogDescription>
                为用户配置数据访问范围
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="user_id">用户ID *</Label>
                <Input
                  id="user_id"
                  type="number"
                  value={createForm.user_id || ''}
                  onChange={(e) => setCreateForm({ ...createForm, user_id: parseInt(e.target.value) || 0 })}
                  placeholder="输入用户ID"
                />
              </div>
              <div>
                <Label htmlFor="resource_type">资源类型 *</Label>
                <Select
                  value={createForm.resource_type}
                  onValueChange={(value) => setCreateForm({ ...createForm, resource_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {resourceTypeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="scope">数据范围 *</Label>
                <Select
                  value={createForm.scope}
                  onValueChange={(value: DataScope) => setCreateForm({ ...createForm, scope: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {dataScopeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        <div>
                          <div>{option.label}</div>
                          <div className="text-xs text-muted-foreground">{option.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
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
      </div>

      {/* 说明卡片 */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Database className="h-4 w-4" />
            数据权限说明
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <ul className="space-y-1">
            <li>• <strong>全部数据</strong>：用户可以访问该资源的所有数据</li>
            <li>• <strong>本部门</strong>：用户只能访问本部门的数据</li>
            <li>• <strong>本人</strong>：用户只能访问自己创建的数据</li>
            <li>• <strong>自定义</strong>：根据配置的部门和用户进行过滤</li>
          </ul>
        </CardContent>
      </Card>

      {/* 数据权限列表 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>权限配置列表</CardTitle>
              <CardDescription>
                已配置的数据权限规则
              </CardDescription>
            </div>
            <Select value={selectedResourceType} onValueChange={setSelectedResourceType}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="选择资源类型" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">所有资源</SelectItem>
                {resourceTypeOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : !dataPermissions || dataPermissions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无数据权限配置
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>用户ID</TableHead>
                  <TableHead>资源类型</TableHead>
                  <TableHead>数据范围</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dataPermissions.map((permission) => (
                  <TableRow key={permission.id}>
                    <TableCell className="font-medium">{permission.user_id}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{getResourceTypeLabel(permission.resource_type)}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge>{getScopeLabel(permission.scope)}</Badge>
                      {permission.scope === 'custom' && (
                        <div className="text-xs text-muted-foreground mt-1">
                          {permission.department_ids && permission.department_ids.length > 0 && (
                            <span>部门: {permission.department_ids.length} 个</span>
                          )}
                          {permission.user_ids && permission.user_ids.length > 0 && (
                            <span className="ml-2">用户: {permission.user_ids.length} 个</span>
                          )}
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(permission.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleEdit(permission)}
                          title="编辑"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => setDeleteId(permission.id)}
                          title="删除"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* 编辑对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent onClose={() => setIsEditDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>编辑数据权限</DialogTitle>
            <DialogDescription>
              修改数据访问范围配置
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_resource_type">资源类型</Label>
              <Select
                value={editForm.resource_type}
                onValueChange={(value) => setEditForm({ ...editForm, resource_type: value })}
                disabled
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {resourceTypeOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit_scope">数据范围</Label>
              <Select
                value={editForm.scope}
                onValueChange={(value: DataScope) => setEditForm({ ...editForm, scope: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {dataScopeOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      <div>
                        <div>{option.label}</div>
                        <div className="text-xs text-muted-foreground">{option.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? '更新中...' : '更新'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认对话框 */}
      <Dialog open={deleteId !== null} onOpenChange={() => setDeleteId(null)}>
        <DialogContent onClose={() => setDeleteId(null)}>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除此数据权限配置吗？删除后，用户将恢复默认的访问权限。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? '删除中...' : '确认删除'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
