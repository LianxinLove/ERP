/**
 * 权限管理页面
 * @description 管理系统权限列表
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { permissionApi } from '@/api/rbac';
import type { Permission, PermissionCreate, PermissionUpdate } from '@/types/rbac';
import { Plus, Edit, Trash2, MoreVertical, Download, Upload } from 'lucide-react';
import { toast } from 'sonner';

export default function PermissionsPage() {
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [editingPermission, setEditingPermission] = useState<Permission | null>(null);
  const [selectedModule, setSelectedModule] = useState<string>('all');

  // 创建表单状态
  const [createForm, setCreateForm] = useState<PermissionCreate>({
    name: '',
    code: '',
    module: '',
    description: '',
  });

  // 编辑表单状态
  const [editForm, setEditForm] = useState<PermissionUpdate>({
    name: '',
    description: '',
  });

  // 导入表单状态
  const [importJson, setImportJson] = useState('');
  const [overwrite, setOverwrite] = useState(false);

  // 获取权限列表
  const { data: permissions, isLoading } = useQuery({
    queryKey: ['permissions', selectedModule],
    queryFn: () => permissionApi.getPermissions(selectedModule === 'all' ? undefined : selectedModule),
  });

  // 获取模块列表
  const modules = React.useMemo(() => {
    if (!permissions) return [];
    const uniqueModules = [...new Set(permissions.map(p => p.module))];
    return uniqueModules.sort();
  }, [permissions]);

  // 创建权限
  const createMutation = useMutation({
    mutationFn: (data: PermissionCreate) => permissionApi.createPermission(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] });
      setIsCreateDialogOpen(false);
      toast.success('权限创建成功');
      resetCreateForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '创建失败');
    },
  });

  // 更新权限
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: PermissionUpdate }) =>
      permissionApi.updatePermission(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] });
      setIsEditDialogOpen(false);
      toast.success('权限更新成功');
      setEditingPermission(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '更新失败');
    },
  });

  // 删除权限
  const deleteMutation = useMutation({
    mutationFn: (id: number) => permissionApi.deletePermission(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] });
      setDeleteId(null);
      toast.success('权限删除成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '删除失败');
    },
  });

  // 导入权限
  const importMutation = useMutation({
    mutationFn: (data: { permissions: PermissionCreate[]; overwrite: boolean }) =>
      permissionApi.importPermissions(data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['permissions'] });
      setIsImportDialogOpen(false);
      toast.success(`导入成功：创建 ${result.created} 条，更新 ${result.updated} 条，跳过 ${result.skipped} 条`);
      setImportJson('');
      setOverwrite(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '导入失败');
    },
  });

  // 导出权限
  const handleExport = async () => {
    try {
      const data = await permissionApi.exportPermissions();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `permissions-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('权限导出成功');
    } catch (error: any) {
      toast.error('导出失败');
    }
  };

  const resetCreateForm = () => {
    setCreateForm({
      name: '',
      code: '',
      module: '',
      description: '',
    });
  };

  const handleCreate = () => {
    if (!createForm.name) {
      toast.error('请输入权限名称');
      return;
    }
    if (!createForm.code) {
      toast.error('请输入权限编码');
      return;
    }
    if (!createForm.module) {
      toast.error('请输入模块名称');
      return;
    }

    createMutation.mutate(createForm);
  };

  const handleEdit = (permission: Permission) => {
    setEditingPermission(permission);
    setEditForm({
      name: permission.name,
      description: permission.description || '',
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

  const handleImport = () => {
    try {
      const data = JSON.parse(importJson);
      if (!Array.isArray(data)) {
        toast.error('导入数据必须是数组格式');
        return;
      }

      importMutation.mutate({
        permissions: data,
        overwrite,
      });
    } catch (error) {
      toast.error('JSON 格式错误');
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">权限管理</h1>
          <p className="text-muted-foreground mt-1">
            管理系统权限和访问控制
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            导出
          </Button>
          <Button variant="outline" onClick={() => setIsImportDialogOpen(true)}>
            <Upload className="h-4 w-4 mr-2" />
            导入
          </Button>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                新建权限
              </Button>
            </DialogTrigger>
            <DialogContent onClose={() => setIsCreateDialogOpen(false)}>
              <DialogHeader>
                <DialogTitle>新建权限</DialogTitle>
                <DialogDescription>
                  创建新的系统权限
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="perm_name">权限名称 *</Label>
                  <Input
                    id="perm_name"
                    value={createForm.name}
                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                    placeholder="如：查看订单"
                  />
                </div>
                <div>
                  <Label htmlFor="perm_code">权限编码 *</Label>
                  <Input
                    id="perm_code"
                    value={createForm.code}
                    onChange={(e) => setCreateForm({ ...createForm, code: e.target.value })}
                    placeholder="如：orders:view"
                  />
                </div>
                <div>
                  <Label htmlFor="perm_module">模块名称 *</Label>
                  <Input
                    id="perm_module"
                    value={createForm.module}
                    onChange={(e) => setCreateForm({ ...createForm, module: e.target.value })}
                    placeholder="如：orders"
                  />
                </div>
                <div>
                  <Label htmlFor="perm_description">描述</Label>
                  <Input
                    id="perm_description"
                    value={createForm.description || ''}
                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                    placeholder="权限描述"
                  />
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
      </div>

      {/* 权限列表 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>权限列表</CardTitle>
              <CardDescription>
                系统中所有权限的列表
              </CardDescription>
            </div>
            <Select value={selectedModule} onValueChange={setSelectedModule}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="选择模块" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">所有模块</SelectItem>
                {modules.map((module) => (
                  <SelectItem key={module} value={module}>
                    {module}
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
          ) : !permissions || permissions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无权限数据
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>权限名称</TableHead>
                  <TableHead>编码</TableHead>
                  <TableHead>模块</TableHead>
                  <TableHead>描述</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {permissions.map((permission) => (
                  <TableRow key={permission.id}>
                    <TableCell className="font-medium">{permission.name}</TableCell>
                    <TableCell>
                      <code className="text-sm bg-muted px-2 py-1 rounded">
                        {permission.code}
                      </code>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{permission.module}</Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {permission.description || '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleEdit(permission)}>
                            <Edit className="h-4 w-4 mr-2" />
                            编辑
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => setDeleteId(permission.id)}
                            className="text-destructive"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            删除
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
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
            <DialogTitle>编辑权限</DialogTitle>
            <DialogDescription>
              修改权限信息
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_perm_name">权限名称 *</Label>
              <Input
                id="edit_perm_name"
                value={editForm.name || ''}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit_perm_description">描述</Label>
              <Input
                id="edit_perm_description"
                value={editForm.description || ''}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              />
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

      {/* 导入对话框 */}
      <Dialog open={isImportDialogOpen} onOpenChange={setIsImportDialogOpen}>
        <DialogContent className="max-w-2xl" onClose={() => setIsImportDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>导入权限</DialogTitle>
            <DialogDescription>
              从 JSON 文件导入权限数据
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="import_json">JSON 数据 *</Label>
              <textarea
                id="import_json"
                value={importJson}
                onChange={(e) => setImportJson(e.target.value)}
                placeholder='[{"name": "查看订单", "code": "orders:view", "module": "订单"}]'
                rows={10}
                className="w-full px-3 py-2 text-sm border rounded-md resize-none"
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="overwrite"
                checked={overwrite}
                onChange={(e) => setOverwrite(e.target.checked)}
                className="h-4 w-4"
              />
              <Label htmlFor="overwrite" className="cursor-pointer">
                覆盖已存在的权限
              </Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsImportDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleImport} disabled={importMutation.isPending}>
              {importMutation.isPending ? '导入中...' : '导入'}
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
              确定要删除此权限吗？删除后，拥有此权限的角色将失去相应访问能力。
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
