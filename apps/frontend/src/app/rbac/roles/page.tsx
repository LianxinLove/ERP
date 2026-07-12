/**
 * 角色管理页面
 * @description 管理系统角色和权限分配
 */

"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
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
import { roleApi, permissionApi } from '@/api/rbac';
import type { Role, RoleListItem, RoleCreate, RoleUpdate, Permission } from '@/types/rbac';
import { Plus, Edit, Trash2, Shield, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';

export default function RolesPage() {
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isPermissionDialogOpen, setIsPermissionDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [permissionRoleId, setPermissionRoleId] = useState<number | null>(null);

  // 创建表单状态
  const [createForm, setCreateForm] = useState<RoleCreate>({
    name: '',
    code: '',
    description: '',
    permission_ids: [],
  });

  // 编辑表单状态
  const [editForm, setEditForm] = useState<RoleUpdate>({
    name: '',
    description: '',
    permission_ids: [],
  });

  // 获取角色列表
  const { data: roles, isLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: roleApi.getRoles,
  });

  // 获取所有权限（用于权限分配）
  const { data: permissions } = useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionApi.getPermissions(),
    enabled: isCreateDialogOpen || isEditDialogOpen || isPermissionDialogOpen,
  });

  // 获取角色详情（包含权限列表）
  const { data: roleDetail } = useQuery({
    queryKey: ['role-detail', permissionRoleId],
    queryFn: () => roleApi.getRole(permissionRoleId!),
    enabled: !!permissionRoleId && isPermissionDialogOpen,
  });

  // 创建角色
  const createMutation = useMutation({
    mutationFn: (data: RoleCreate) => roleApi.createRole(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setIsCreateDialogOpen(false);
      toast.success('角色创建成功');
      resetCreateForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '创建失败');
    },
  });

  // 更新角色
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: RoleUpdate }) =>
      roleApi.updateRole(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setIsEditDialogOpen(false);
      toast.success('角色更新成功');
      setEditingRole(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '更新失败');
    },
  });

  // 删除角色
  const deleteMutation = useMutation({
    mutationFn: (id: number) => roleApi.deleteRole(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      setDeleteId(null);
      toast.success('角色删除成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '删除失败');
    },
  });

  // 分配权限
  const assignPermissionsMutation = useMutation({
    mutationFn: ({ roleId, permissionIds }: { roleId: number; permissionIds: number[] }) =>
      roleApi.assignPermissions(roleId, permissionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      queryClient.invalidateQueries({ queryKey: ['role-detail'] });
      setIsPermissionDialogOpen(false);
      toast.success('权限分配成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '分配失败');
    },
  });

  const resetCreateForm = () => {
    setCreateForm({
      name: '',
      code: '',
      description: '',
      permission_ids: [],
    });
  };

  const handleCreate = () => {
    if (!createForm.name) {
      toast.error('请输入角色名称');
      return;
    }
    if (!createForm.code) {
      toast.error('请输入角色编码');
      return;
    }

    createMutation.mutate(createForm);
  };

  const handleEdit = (role: RoleListItem) => {
    setEditingRole(role as Role);
    setEditForm({
      name: role.name,
      description: role.description || '',
      permission_ids: [],
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!editingRole) return;

    updateMutation.mutate({
      id: editingRole.id,
      data: editForm,
    });
  };

  const confirmDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId);
    }
  };

  const openPermissionDialog = (roleId: number) => {
    setPermissionRoleId(roleId);
    setIsPermissionDialogOpen(true);
  };

  const handlePermissionSave = () => {
    if (!permissionRoleId || !roleDetail) return;

    const selectedPermissions = permissions
      ?.filter(p => (document.getElementById(`perm-${p.id}`) as HTMLInputElement)?.checked)
      .map(p => p.id) || [];

    assignPermissionsMutation.mutate({
      roleId: permissionRoleId,
      permissionIds: selectedPermissions,
    });
  };

  // 按模块分组权限
  const groupedPermissions = React.useMemo(() => {
    if (!permissions) return {};
    return permissions.reduce((acc, perm) => {
      if (!acc[perm.module]) {
        acc[perm.module] = [];
      }
      acc[perm.module].push(perm);
      return acc;
    }, {} as Record<string, Permission[]>);
  }, [permissions]);

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">角色管理</h1>
          <p className="text-muted-foreground mt-1">
            管理系统角色和权限分配
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新建角色
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl" onClose={() => setIsCreateDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>新建角色</DialogTitle>
              <DialogDescription>
                创建新的系统角色
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">角色名称 *</Label>
                <Input
                  id="name"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  placeholder="如：销售人员"
                />
              </div>
              <div>
                <Label htmlFor="code">角色编码 *</Label>
                <Input
                  id="code"
                  value={createForm.code}
                  onChange={(e) => setCreateForm({ ...createForm, code: e.target.value })}
                  placeholder="如：sales_staff"
                />
              </div>
              <div>
                <Label htmlFor="description">描述</Label>
                <Textarea
                  id="description"
                  value={createForm.description || ''}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  placeholder="角色描述"
                  rows={3}
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

      {/* 角色列表 */}
      <Card>
        <CardHeader>
          <CardTitle>角色列表</CardTitle>
          <CardDescription>
            系统中所有角色的列表，系统角色不可修改和删除
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : !roles || roles.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无角色数据
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>角色名称</TableHead>
                  <TableHead>编码</TableHead>
                  <TableHead>描述</TableHead>
                  <TableHead>权限数量</TableHead>
                  <TableHead>类型</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {roles.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell className="font-medium">{role.name}</TableCell>
                    <TableCell>
                      <code className="text-sm bg-muted px-2 py-1 rounded">
                        {role.code}
                      </code>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {role.description || '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {role.permission_count || 0} 个权限
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {role.is_system ? (
                        <Badge variant="outline">系统角色</Badge>
                      ) : (
                        <Badge>自定义角色</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => openPermissionDialog(role.id)}
                          title="分配权限"
                        >
                          <ShieldCheck className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => handleEdit(role)}
                          disabled={role.is_system}
                          title="编辑"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => setDeleteId(role.id)}
                          disabled={role.is_system}
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
            <DialogTitle>编辑角色</DialogTitle>
            <DialogDescription>
              修改角色信息
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_name">角色名称 *</Label>
              <Input
                id="edit_name"
                value={editForm.name || ''}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit_description">描述</Label>
              <Textarea
                id="edit_description"
                value={editForm.description || ''}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                rows={3}
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

      {/* 权限分配对话框 */}
      <Dialog open={isPermissionDialogOpen} onOpenChange={setIsPermissionDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto" onClose={() => setIsPermissionDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>分配权限</DialogTitle>
            <DialogDescription>
              为角色选择可访问的权限
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {Object.entries(groupedPermissions).map(([module, modulePermissions]) => (
              <div key={module}>
                <h3 className="font-medium mb-2 flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  {module}
                </h3>
                <div className="space-y-2 pl-6">
                  {modulePermissions.map((permission) => {
                    const isChecked = roleDetail?.permissions?.some(p => p.id === permission.id);
                    return (
                      <div key={permission.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={`perm-${permission.id}`}
                          defaultChecked={isChecked}
                        />
                        <Label
                          htmlFor={`perm-${permission.id}`}
                          className="cursor-pointer"
                        >
                          {permission.name}
                          <span className="text-muted-foreground ml-2">
                            ({permission.code})
                          </span>
                        </Label>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsPermissionDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handlePermissionSave} disabled={assignPermissionsMutation.isPending}>
              {assignPermissionsMutation.isPending ? '保存中...' : '保存'}
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
              确定要删除此角色吗？删除后，拥有该角色的用户将失去相应权限。
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
