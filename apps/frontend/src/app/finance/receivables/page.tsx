/**
 * 应收账款管理页面
 * @description 应收账款列表和管理
 */

"use client";

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { financeApi } from '@/api/finance';
import type { ReceivableResponse, ReceivableCreate, ReceivableStatus } from '@/types/finance';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Plus, Search, Trash2, Eye } from 'lucide-react';
import { toast } from 'sonner';

/** 应收账款状态标签颜色 */
const statusColors: Record<ReceivableStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  partial_paid: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  paid: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  overdue: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  write_off: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
};

/** 应收账款状态文本 */
const statusText: Record<ReceivableStatus, string> = {
  pending: '待收款',
  partial_paid: '部分收款',
  paid: '已收款',
  overdue: '逾期',
  write_off: '坏账核销',
};

export default function ReceivablesPage() {
  const queryClient = useQueryClient();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // 创建表单状态
  const [createForm, setCreateForm] = useState<ReceivableCreate>({
    customer_id: 0,
    sales_order_id: undefined,
    amount: 0,
    due_date: undefined,
    notes: '',
  });

  // 获取应收账款列表
  const { data: receivables, isLoading } = useQuery<ReceivableResponse[]>({
    queryKey: ['receivables', statusFilter, searchKeyword],
    queryFn: () => financeApi.getReceivables({
      status: statusFilter,
      keyword: searchKeyword || undefined,
    }),
  });

  // 创建应收账款
  const createMutation = useMutation({
    mutationFn: (data: ReceivableCreate) => financeApi.createReceivable(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['receivables'] });
      queryClient.invalidateQueries({ queryKey: ['finance-summary'] });
      setIsCreateDialogOpen(false);
      toast.success('应收账款创建成功');
      setCreateForm({
        customer_id: 0,
        sales_order_id: undefined,
        amount: 0,
        due_date: undefined,
        notes: '',
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '创建失败');
    },
  });

  // 删除应收账款
  const deleteMutation = useMutation({
    mutationFn: (id: number) => financeApi.deleteReceivable(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['receivables'] });
      queryClient.invalidateQueries({ queryKey: ['finance-summary'] });
      setDeleteId(null);
      toast.success('删除成功');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '删除失败');
    },
  });

  const handleCreate = () => {
    if (!createForm.customer_id) {
      toast.error('请选择客户');
      return;
    }
    if (createForm.amount <= 0) {
      toast.error('金额必须大于0');
      return;
    }
    createMutation.mutate(createForm);
  };

  const handleDelete = (id: number) => {
    setDeleteId(id);
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
          <h1 className="text-2xl font-bold tracking-tight">应收账款</h1>
          <p className="text-muted-foreground mt-1">
            管理客户应收款项
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新建应收账款
            </Button>
          </DialogTrigger>
          <DialogContent onClose={() => setIsCreateDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>新建应收账款</DialogTitle>
              <DialogDescription>
                创建新的应收账款记录
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="customer_id">客户ID *</Label>
                <Input
                  id="customer_id"
                  type="number"
                  value={createForm.customer_id}
                  onChange={(e) => setCreateForm({ ...createForm, customer_id: Number(e.target.value) })}
                  placeholder="输入客户ID"
                />
              </div>
              <div>
                <Label htmlFor="sales_order_id">销售订单ID（可选）</Label>
                <Input
                  id="sales_order_id"
                  type="number"
                  value={createForm.sales_order_id || ''}
                  onChange={(e) => setCreateForm({
                    ...createForm,
                    sales_order_id: e.target.value ? Number(e.target.value) : undefined,
                  })}
                  placeholder="输入销售订单ID"
                />
              </div>
              <div>
                <Label htmlFor="amount">金额 *</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={createForm.amount || ''}
                  onChange={(e) => setCreateForm({ ...createForm, amount: Number(e.target.value) })}
                  placeholder="输入金额"
                />
              </div>
              <div>
                <Label htmlFor="due_date">到期日期（可选）</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={createForm.due_date || ''}
                  onChange={(e) => setCreateForm({ ...createForm, due_date: e.target.value || undefined })}
                />
              </div>
              <div>
                <Label htmlFor="notes">备注</Label>
                <Input
                  id="notes"
                  value={createForm.notes || ''}
                  onChange={(e) => setCreateForm({ ...createForm, notes: e.target.value })}
                  placeholder="输入备注"
                />
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
              >
                取消
              </Button>
              <Button
                onClick={handleCreate}
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? '创建中...' : '创建'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* 筛选和搜索 */}
      <Card>
        <CardHeader>
          <CardTitle>筛选条件</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="搜索单号..."
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-input bg-background rounded-md px-3 py-2 text-sm"
            >
              <option value="">全部状态</option>
              <option value="pending">待收款</option>
              <option value="partial_paid">部分收款</option>
              <option value="paid">已收款</option>
              <option value="overdue">逾期</option>
              <option value="write_off">坏账核销</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 应收账款列表 */}
      <Card>
        <CardHeader>
          <CardTitle>应收账款列表</CardTitle>
          <CardDescription>
            共 {receivables?.length || 0} 条记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : !receivables || receivables.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无数据
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>单号</TableHead>
                  <TableHead>客户ID</TableHead>
                  <TableHead>金额</TableHead>
                  <TableHead>已收金额</TableHead>
                  <TableHead>剩余金额</TableHead>
                  <TableHead>到期日期</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {receivables.map((receivable) => (
                  <TableRow key={receivable.id}>
                    <TableCell className="font-medium">{receivable.receivable_no}</TableCell>
                    <TableCell>{receivable.customer_id}</TableCell>
                    <TableCell>{formatCurrency(receivable.amount)}</TableCell>
                    <TableCell>{formatCurrency(receivable.paid_amount)}</TableCell>
                    <TableCell>{formatCurrency(receivable.remaining_amount)}</TableCell>
                    <TableCell>{receivable.due_date ? formatDate(receivable.due_date) : '-'}</TableCell>
                    <TableCell>
                      <Badge className={statusColors[receivable.status]}>
                        {statusText[receivable.status]}
                      </Badge>
                    </TableCell>
                    <TableCell>{formatDate(receivable.created_at)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="icon" asChild>
                          <a href={`/finance/receivables/${receivable.id}`}>
                            <Eye className="h-4 w-4" />
                          </a>
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(receivable.id)}
                          disabled={receivable.paid_amount > 0}
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

      {/* 删除确认对话框 */}
      <Dialog open={deleteId !== null} onOpenChange={() => setDeleteId(null)}>
        <DialogContent onClose={() => setDeleteId(null)}>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除这条应收账款记录吗？此操作不可撤销。
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
