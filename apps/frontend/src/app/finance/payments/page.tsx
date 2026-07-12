/**
 * 收付款记录管理页面
 * @description 收付款记录列表和管理
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { financeApi } from '@/api/finance';
import type { PaymentResponse, PaymentCreate, PaymentType, PaymentStatus } from '@/types/finance';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Plus, Search, Eye, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

/** 收付款状态标签颜色 */
const statusColors: Record<PaymentStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  cancelled: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200',
};

/** 收付款状态文本 */
const statusText: Record<PaymentStatus, string> = {
  pending: '待处理',
  completed: '已完成',
  cancelled: '已取消',
};

/** 收付款类型文本 */
const paymentTypeText: Record<PaymentType, string> = {
  receipt: '收款',
  payment: '付款',
};

export default function PaymentsPage() {
  const queryClient = useQueryClient();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  // 创建表单状态
  const [createForm, setCreateForm] = useState<PaymentCreate>({
    payment_type: 'receipt',
    receivable_id: undefined,
    payable_id: undefined,
    amount: 0,
    payment_method_id: undefined,
    payment_date: new Date().toISOString().split('T')[0],
    reference_no: '',
    notes: '',
    status: 'pending',
  });

  // 获取收付款记录列表
  const { data: payments, isLoading } = useQuery<PaymentResponse[]>({
    queryKey: ['payments', typeFilter, statusFilter, searchKeyword],
    queryFn: () => financeApi.getPayments({
      payment_type: typeFilter as PaymentType || undefined,
      status: statusFilter as PaymentStatus || undefined,
      keyword: searchKeyword || undefined,
    }),
  });

  // 创建收付款记录
  const createMutation = useMutation({
    mutationFn: (data: PaymentCreate) => financeApi.createPayment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['finance-summary'] });
      queryClient.invalidateQueries({ queryKey: ['receivables'] });
      queryClient.invalidateQueries({ queryKey: ['payables'] });
      setIsCreateDialogOpen(false);
      toast.success('收付款记录创建成功');
      resetCreateForm();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '创建失败');
    },
  });

  // 完成收付款
  const completeMutation = useMutation({
    mutationFn: (id: number) => financeApi.completePayment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['finance-summary'] });
      toast.success('已完成');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '操作失败');
    },
  });

  // 取消收付款
  const cancelMutation = useMutation({
    mutationFn: (id: number) => financeApi.cancelPayment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      toast.success('已取消');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '操作失败');
    },
  });

  const resetCreateForm = () => {
    setCreateForm({
      payment_type: 'receipt',
      receivable_id: undefined,
      payable_id: undefined,
      amount: 0,
      payment_method_id: undefined,
      payment_date: new Date().toISOString().split('T')[0],
      reference_no: '',
      notes: '',
      status: 'pending',
    });
  };

  const handleCreate = () => {
    const isReceipt = createForm.payment_type === 'receipt';

    if (isReceipt && !createForm.receivable_id) {
      toast.error('请选择应收账款');
      return;
    }
    if (!isReceipt && !createForm.payable_id) {
      toast.error('请选择应付账款');
      return;
    }
    if (createForm.amount <= 0) {
      toast.error('金额必须大于0');
      return;
    }

    createMutation.mutate(createForm);
  };

  const handleComplete = (id: number) => {
    completeMutation.mutate(id);
  };

  const handleCancel = (id: number) => {
    cancelMutation.mutate(id);
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">收付款记录</h1>
          <p className="text-muted-foreground mt-1">
            查看和管理收付款记录
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新建收付款记录
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md" onClose={() => setIsCreateDialogOpen(false)}>
            <DialogHeader>
              <DialogTitle>新建收付款记录</DialogTitle>
              <DialogDescription>
                创建新的收付款记录
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="payment_type">收付款类型 *</Label>
                <Select
                  value={createForm.payment_type}
                  onValueChange={(value: PaymentType) => {
                    setCreateForm({
                      ...createForm,
                      payment_type: value,
                      receivable_id: value === 'payment' ? undefined : createForm.receivable_id,
                      payable_id: value === 'receipt' ? undefined : createForm.payable_id,
                    });
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="receipt">收款</SelectItem>
                    <SelectItem value="payment">付款</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {createForm.payment_type === 'receipt' ? (
                <div>
                  <Label htmlFor="receivable_id">应收账款ID *</Label>
                  <Input
                    id="receivable_id"
                    type="number"
                    value={createForm.receivable_id || ''}
                    onChange={(e) => setCreateForm({
                      ...createForm,
                      receivable_id: e.target.value ? Number(e.target.value) : undefined,
                    })}
                    placeholder="输入应收账款ID"
                  />
                </div>
              ) : (
                <div>
                  <Label htmlFor="payable_id">应付账款ID *</Label>
                  <Input
                    id="payable_id"
                    type="number"
                    value={createForm.payable_id || ''}
                    onChange={(e) => setCreateForm({
                      ...createForm,
                      payable_id: e.target.value ? Number(e.target.value) : undefined,
                    })}
                    placeholder="输入应付账款ID"
                  />
                </div>
              )}

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
                <Label htmlFor="payment_method_id">付款方式ID（可选）</Label>
                <Input
                  id="payment_method_id"
                  type="number"
                  value={createForm.payment_method_id || ''}
                  onChange={(e) => setCreateForm({
                    ...createForm,
                    payment_method_id: e.target.value ? Number(e.target.value) : undefined,
                  })}
                  placeholder="输入付款方式ID"
                />
              </div>

              <div>
                <Label htmlFor="payment_date">收付款日期 *</Label>
                <Input
                  id="payment_date"
                  type="date"
                  value={createForm.payment_date}
                  onChange={(e) => setCreateForm({ ...createForm, payment_date: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="reference_no">参考号（可选）</Label>
                <Input
                  id="reference_no"
                  value={createForm.reference_no || ''}
                  onChange={(e) => setCreateForm({ ...createForm, reference_no: e.target.value })}
                  placeholder="输入参考号/支票号"
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
                onClick={() => {
                  setIsCreateDialogOpen(false);
                  resetCreateForm();
                }}
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
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="border border-input bg-background rounded-md px-3 py-2 text-sm"
            >
              <option value="">全部类型</option>
              <option value="receipt">收款</option>
              <option value="payment">付款</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-input bg-background rounded-md px-3 py-2 text-sm"
            >
              <option value="">全部状态</option>
              <option value="pending">待处理</option>
              <option value="completed">已完成</option>
              <option value="cancelled">已取消</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* 收付款记录列表 */}
      <Card>
        <CardHeader>
          <CardTitle>收付款记录列表</CardTitle>
          <CardDescription>
            共 {payments?.length || 0} 条记录
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              加载中...
            </div>
          ) : !payments || payments.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              暂无数据
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>单号</TableHead>
                  <TableHead>类型</TableHead>
                  <TableHead>关联单据ID</TableHead>
                  <TableHead>金额</TableHead>
                  <TableHead>收付款日期</TableHead>
                  <TableHead>参考号</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>创建时间</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {payments.map((payment) => (
                  <TableRow key={payment.id}>
                    <TableCell className="font-medium">{payment.payment_no}</TableCell>
                    <TableCell>
                      <Badge variant={payment.payment_type === 'receipt' ? 'default' : 'secondary'}>
                        {paymentTypeText[payment.payment_type]}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {payment.receivable_id || payment.payable_id ? (
                        <span className="text-sm text-muted-foreground">
                          {payment.receivable_id ? `应收: ${payment.receivable_id}` : `应付: ${payment.payable_id}`}
                        </span>
                      ) : '-'}
                    </TableCell>
                    <TableCell>{formatCurrency(payment.amount)}</TableCell>
                    <TableCell>{formatDate(payment.payment_date)}</TableCell>
                    <TableCell>{payment.reference_no || '-'}</TableCell>
                    <TableCell>
                      <Badge className={statusColors[payment.status]}>
                        {statusText[payment.status]}
                      </Badge>
                    </TableCell>
                    <TableCell>{formatDate(payment.created_at)}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="icon" asChild>
                          <a href={`/finance/payments/${payment.id}`}>
                            <Eye className="h-4 w-4" />
                          </a>
                        </Button>
                        {payment.status === 'pending' && (
                          <>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleComplete(payment.id)}
                              disabled={completeMutation.isPending}
                            >
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleCancel(payment.id)}
                              disabled={cancelMutation.isPending}
                            >
                              <XCircle className="h-4 w-4 text-destructive" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
