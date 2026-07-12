/**
 * 用户角色分配页面
 * @description 为用户分配和管理角色
 */

"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
import { roleApi, userRoleApi } from '@/api/rbac';
import type { Role, User } from '@/types/rbac';
import { UserPlus, Shield, Trash2, Search } from 'lucide-react';
import { toast } from 'sonner';

// 临时用户数据类型（实际应从用户API获取）
interface UserData extends User {
  roles?: Role[];
}

export default function UserRolesPage() {
  const queryClient = useQueryClient();
  const [isAssignDialogOpen, setIsAssignDialogOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // 获取角色列表
  const { data: roles, isLoading: rolesLoading } = useQuery({
    queryKey: ['roles'],
    queryFn: roleApi.getRoles,
  });

  // 模拟用户数据（实际应从后端API获取）
  const { data: users = mockUsers, isLoading: usersLoading } = useQuery({
    queryKey: ['users'],
    queryFn: () => Promise.resolve(mockUsers),
  });

  // 分配角色 mutation
  const assignRolesMutation = useMutation({
    mutationFn: ({ userId, roleIds }: { userId: number; roleIds: number[] }) =>
      userRoleApi.assignUserRoles(userId, { role_ids: roleIds }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsAssignDialogOpen(false);
      toast.success('角色分配成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || '分配失败');
    },
  });

  // 获取用户角色
  const { data: userRoles, isLoading: userRolesLoading } = useQuery({
    queryKey: ['user-roles', selectedUserId],
    queryFn: () => userRoleApi.getUserRoles(selectedUserId!),
    enabled: !!selectedUserId && isAssignDialogOpen,
  });

  // 过滤用户
  const filteredUsers = React.useMemo(() => {
    if (!searchQuery) return users;
    const query = searchQuery.toLowerCase();
    return users.filter(
      (user) =>
        user.username.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query) ||
        user.full_name?.toLowerCase().includes(query)
    );
  }, [users, searchQuery]);

  const openAssignDialog = (userId: number) => {
    setSelectedUserId(userId);
    setIsAssignDialogOpen(true);
  };

  const handleSaveRoles = () => {
    if (!selectedUserId) return;

    const selectedRoleIds = Array.from(
      document.querySelectorAll<HTMLInputElement>('[name="role-checkbox"]:checked')
    ).map((checkbox) => parseInt((checkbox as HTMLInputElement).value));

    assignRolesMutation.mutate({
      userId: selectedUserId,
      roleIds: selectedRoleIds,
    });
  };

  // 获取用户当前角色
  const getUserRoles = (userId: number) => {
    // 实际应从API获取，这里用模拟数据
    return mockUserData.find((u) => u.id === userId)?.roles || [];
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">用户角色分配</h1>
          <p className="text-muted-foreground mt-1">
            为用户分配和管理角色
          </p>
        </div>
      </div>

      {/* 搜索栏 */}
      <Card>
        <CardHeader>
          <CardTitle>用户列表</CardTitle>
          <CardDescription>
            选择用户进行角色分配
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索用户名、邮箱或姓名..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {usersLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {searchQuery ? '没有找到匹配的用户' : '暂无用户数据'}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>用户名</TableHead>
                  <TableHead>邮箱</TableHead>
                  <TableHead>姓名</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>角色</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => {
                  const userRolesList = getUserRoles(user.id);
                  return (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.username}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.full_name || '-'}</TableCell>
                      <TableCell>
                        {user.is_active ? (
                          <Badge variant="default">活跃</Badge>
                        ) : (
                          <Badge variant="secondary">停用</Badge>
                        )}
                        {user.is_superuser && (
                          <Badge variant="outline" className="ml-2">
                            超级管理员
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {userRolesList.length === 0 ? (
                            <span className="text-muted-foreground text-sm">无角色</span>
                          ) : (
                            userRolesList.map((role) => (
                              <Badge key={role.id} variant="secondary">
                                {role.name}
                              </Badge>
                            ))
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openAssignDialog(user.id)}
                        >
                          <Shield className="h-4 w-4 mr-2" />
                          分配角色
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* 角色分配对话框 */}
      <Dialog open={isAssignDialogOpen} onOpenChange={setIsAssignDialogOpen}>
        <DialogContent className="max-w-md" onClose={() => setIsAssignDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>分配角色</DialogTitle>
            <DialogDescription>
              为用户选择角色
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {rolesLoading || userRolesLoading ? (
              <div className="text-center py-4 text-muted-foreground">
                加载中...
              </div>
            ) : (
              <div className="space-y-2">
                {roles?.map((role) => {
                  const hasRole = userRoles?.some((r) => r.id === role.id);
                  return (
                    <div key={role.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`role-dialog-${role.id}`}
                        name="role-checkbox"
                        value={role.id}
                        defaultChecked={hasRole}
                        disabled={role.is_system}
                      />
                      <Label
                        htmlFor={`role-dialog-${role.id}`}
                        className="flex-1 cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <span>{role.name}</span>
                          {role.is_system && (
                            <Badge variant="outline" className="text-xs">
                              系统角色
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {role.description || role.code}
                        </p>
                      </Label>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAssignDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSaveRoles} disabled={assignRolesMutation.isPending}>
              {assignRolesMutation.isPending ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// 模拟用户数据（实际应从用户API获取）
const mockUsers: UserData[] = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: '系统管理员',
    is_active: true,
    is_superuser: true,
    created_at: '2024-01-01T00:00:00Z',
    roles: [],
  },
  {
    id: 2,
    username: 'sales_manager',
    email: 'sales.manager@example.com',
    full_name: '销售经理',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-02T00:00:00Z',
    roles: [],
  },
  {
    id: 3,
    username: 'sales_staff',
    email: 'sales.staff@example.com',
    full_name: '销售人员',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-03T00:00:00Z',
    roles: [],
  },
  {
    id: 4,
    username: 'warehouse_manager',
    email: 'warehouse.manager@example.com',
    full_name: '仓库经理',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-04T00:00:00Z',
    roles: [],
  },
];

// 模拟用户角色数据
const mockUserData: Array<UserData & { roles: Role[] }> = [
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    full_name: '系统管理员',
    is_active: true,
    is_superuser: true,
    created_at: '2024-01-01T00:00:00Z',
    roles: [],
  },
  {
    id: 2,
    username: 'sales_manager',
    email: 'sales.manager@example.com',
    full_name: '销售经理',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-02T00:00:00Z',
    roles: [
      { id: 1, name: '销售经理', code: 'sales_manager', is_system: false, created_at: '', updated_at: '' },
    ],
  },
  {
    id: 3,
    username: 'sales_staff',
    email: 'sales.staff@example.com',
    full_name: '销售人员',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-03T00:00:00Z',
    roles: [
      { id: 2, name: '销售人员', code: 'sales_staff', is_system: false, created_at: '', updated_at: '' },
    ],
  },
  {
    id: 4,
    username: 'warehouse_manager',
    email: 'warehouse.manager@example.com',
    full_name: '仓库经理',
    is_active: true,
    is_superuser: false,
    created_at: '2024-01-04T00:00:00Z',
    roles: [],
  },
];
