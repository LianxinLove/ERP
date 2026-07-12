/**
 * 会计科目管理页面
 * @description 会计科目树形管理和维护
 */

"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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
import { financeApi } from '@/api/finance';
import type { AccountTree, AccountCreate, AccountUpdate, AccountType } from '@/types/finance';
import { Plus, Edit, Trash2, ChevronRight, ChevronDown } from 'lucide-react';
import { toast } from 'sonner';

/** 科目类型标签颜色 */
const accountTypeColors: Record<AccountType, string> = {
  asset: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  liability: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  equity: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
  revenue: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  expense: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
};

/** 科目类型文本 */
const accountTypeText: Record<AccountType, string> = {
  asset: '资产',
  liability: '负债',
  equity: '所有者权益',
  revenue: '收入',
  expense: '费用',
};

/** 科目树节点组件 */
interface AccountTreeNodeProps {
  node: AccountTree;
  level: number;
  onEdit: (node: AccountTree) => void;
  onDelete: (id: number) => void;
  onCreateChild: (parentId: number) => void;
}

const AccountTreeNode: React.FC<AccountTreeNodeProps> = ({
  node,
  level,
  onEdit,
  onDelete,
  onCreateChild,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div>
      <div
        className="flex items-center gap-2 py-2 px-3 hover:bg-muted/50 rounded-md transition-colors"
        style={{ paddingLeft: `${level * 20 + 12}px` }}
      >
        {hasChildren ? (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-muted rounded"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : (
          <div className="w-6" />
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-medium">{node.code}</span>
            <span className="text-sm text-muted-foreground truncate">{node.name}</span>
            <Badge className={accountTypeColors[node.account_type]}>
              {accountTypeText[node.account_type]}
            </Badge>
            {!node.is_active && (
              <Badge variant="outline" className="text-muted-foreground">
                已停用
              </Badge>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onCreateChild(node.id)}
          >
            <Plus className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onEdit(node)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => onDelete(node.id)}
            disabled={!node.is_active}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children.map((child) => (
            <AccountTreeNode
              key={child.id}
              node={child}
              level={level + 1}
              onEdit={onEdit}
              onDelete={onDelete}
              onCreateChild={onCreateChild}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default function AccountsPage() {
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [editingNode, setEditingNode] = useState<AccountTree | null>(null);
  const [parentForCreate, setParentForCreate] = useState<number | null>(null);

  // 创建表单状态
  const [createForm, setCreateForm] = useState<Omit<AccountCreate, 'account_type'> & { account_type: string }>({
    code: '',
    name: '',
    account_type: 'asset',
    parent_id: undefined,
    description: '',
    is_active: true,
  });

  // 编辑表单状态
  const [editForm, setEditForm] = useState<AccountUpdate>({
    name: '',
    account_type: undefined,
    parent_id: undefined,
    description: undefined,
    is_active: undefined,
  });

  // 获取科目树
  const { data: accountTree, isLoading } = useQuery<AccountTree[]>({
    queryKey: ['account-tree'],
    queryFn: financeApi.getAccountTree,
  });

  // 创建科目
  const createMutation = useMutation({
    mutationFn: (data: AccountCreate) => financeApi.createAccount(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['account-tree'] });
      setIsCreateDialogOpen(false);
      toast.success('科目创建成功');
      resetCreateForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '创建失败');
    },
  });

  // 更新科目
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: AccountUpdate }) =>
      financeApi.updateAccount(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['account-tree'] });
      setIsEditDialogOpen(false);
      toast.success('科目更新成功');
      setEditingNode(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '更新失败');
    },
  });

  // 删除科目
  const deleteMutation = useMutation({
    mutationFn: (id: number) => financeApi.deleteAccount(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['account-tree'] });
      setDeleteId(null);
      toast.success('科目删除成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '删除失败');
    },
  });

  const resetCreateForm = () => {
    setCreateForm({
      code: '',
      name: '',
      account_type: 'asset',
      parent_id: undefined,
      level: 1,
      description: '',
      is_active: true,
    });
    setParentForCreate(null);
  };

  const handleCreate = () => {
    if (!createForm.code) {
      toast.error('请输入科目编码');
      return;
    }
    if (!createForm.name) {
      toast.error('请输入科目名称');
      return;
    }

    const data = {
      ...createForm,
      parent_id: parentForCreate,
      level: parentForCreate ? 2 : 1,
    };

    createMutation.mutate(data);
  };

  const handleEdit = (node: AccountTree) => {
    setEditingNode(node);
    setEditForm({
      name: node.name,
      account_type: node.account_type,
      parent_id: node.parent_id,
      description: node.description || undefined,
      is_active: node.is_active,
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdate = () => {
    if (!editingNode) return;

    updateMutation.mutate({
      id: editingNode.id,
      data: editForm,
    });
  };

  const confirmDelete = () => {
    if (deleteId) {
      deleteMutation.mutate(deleteId);
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">会计科目</h1>
          <p className="text-muted-foreground mt-1">
            管理会计科目体系
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新建科目
            </Button>
          </DialogTrigger>
          <DialogContent onClose={() => setIsCreateDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>新建会计科目</DialogTitle>
              <DialogDescription>
                创建新的会计科目
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="code">科目编码 *</Label>
                <Input
                  id="code"
                  value={createForm.code}
                  onChange={(e) => setCreateForm({ ...createForm, code: e.target.value })}
                  placeholder="如：1001"
                />
              </div>
              <div>
                <Label htmlFor="name">科目名称 *</Label>
                <Input
                  id="name"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  placeholder="如：库存现金"
                />
              </div>
              <div>
                <Label htmlFor="account_type">科目类型 *</Label>
                <Select
                  value={createForm.account_type}
                  onValueChange={(value: AccountType) =>
                    setCreateForm({ ...createForm, account_type: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="asset">资产</SelectItem>
                    <SelectItem value="liability">负债</SelectItem>
                    <SelectItem value="equity">所有者权益</SelectItem>
                    <SelectItem value="revenue">收入</SelectItem>
                    <SelectItem value="expense">费用</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="description">描述</Label>
                <Input
                  id="description"
                  value={createForm.description || ''}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  placeholder="科目描述"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={createForm.is_active}
                  onChange={(e) => setCreateForm({ ...createForm, is_active: e.target.checked })}
                  className="h-4 w-4"
                />
                <Label htmlFor="is_active" className="cursor-pointer">
                  启用此科目
                </Label>
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

      {/* 科目树 */}
      <Card>
        <CardHeader>
          <CardTitle>科目树</CardTitle>
          <CardDescription>
            点击左侧箭头展开/折叠子科目
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : !accountTree || accountTree.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无科目数据
            </div>
          ) : (
            <div className="border rounded-md divide-y">
              {accountTree.map((node) => (
                <AccountTreeNode
                  key={node.id}
                  node={node}
                  level={0}
                  onEdit={handleEdit}
                  onDelete={(id) => setDeleteId(id)}
                  onCreateChild={(parentId) => {
                    setParentForCreate(parentId);
                    setIsCreateDialogOpen(true);
                  }}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 编辑对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent onClose={() => setIsEditDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle>编辑会计科目</DialogTitle>
            <DialogDescription>
              修改会计科目信息
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit_name">科目名称 *</Label>
              <Input
                id="edit_name"
                value={editForm.name || ''}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit_account_type">科目类型</Label>
              <Select
                value={editForm.account_type}
                onValueChange={(value: AccountType) =>
                  setEditForm({ ...editForm, account_type: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="asset">资产</SelectItem>
                  <SelectItem value="liability">负债</SelectItem>
                  <SelectItem value="equity">所有者权益</SelectItem>
                  <SelectItem value="revenue">收入</SelectItem>
                  <SelectItem value="expense">费用</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit_description">描述</Label>
              <Input
                id="edit_description"
                value={editForm.description || ''}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="edit_is_active"
                checked={editForm.is_active ?? true}
                onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                className="h-4 w-4"
              />
              <Label htmlFor="edit_is_active" className="cursor-pointer">
                启用此科目
              </Label>
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
              确定要删除此科目吗？如果科目下有子科目，则无法删除。
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
