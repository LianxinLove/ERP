/**
 * 客户管理页面
 *
 * @description 管理客户信息的CRUD操作页面
 */

'use client';

import { useState, useEffect, useCallback, memo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Plus, Pencil, Trash2, Search, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { salesApi } from '@/api/sales';
import type { Customer, CreateCustomerRequest, UpdateCustomerRequest } from '@/types/sales';
import { toast } from 'sonner';
import { AlertCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

/**
 * 客户状态徽章
 */
function CustomerStatusBadge({ status }: { status: Customer['status'] }) {
  switch (status) {
    case 'active':
      return <Badge variant="success">正常</Badge>;
    case 'inactive':
      return <Badge variant="secondary">停用</Badge>;
    case 'blacklist':
      return <Badge variant="destructive">黑名单</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

/**
 * 客户表单对话框
 */
interface CustomerFormDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: CreateCustomerRequest | UpdateCustomerRequest) => void;
  customer?: Customer;
  isSubmitting?: boolean;
}

function CustomerFormDialog({ open, onClose, onSubmit, customer, isSubmitting }: CustomerFormDialogProps) {
  const isEdit = !!customer;

  // 初始化表单数据
  const [formData, setFormData] = useState<CreateCustomerRequest>({
    code: '',
    name: '',
    contact: '',
    phone: '',
    email: '',
    address: '',
    tax_number: '',
    bank_name: '',
    bank_account: '',
    credit_limit: undefined,
    payment_terms: undefined,
    notes: '',
    status: 'active',
  });

  // 当 customer 变化时重置表单数据
  useEffect(() => {
    if (open) {
      if (customer) {
        setFormData(customer);
      } else {
        setFormData({
          code: '',
          name: '',
          contact: '',
          phone: '',
          email: '',
          address: '',
          tax_number: '',
          bank_name: '',
          bank_account: '',
          credit_limit: undefined,
          payment_terms: undefined,
          notes: '',
          status: 'active',
        });
      }
    }
  }, [customer, open]); // 只在 open 或 customer 变化时重置

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  }, [formData, onSubmit]);

  const handleChange = useCallback((field: keyof CreateCustomerRequest, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleCloseDialog = useCallback(() => {
    onClose();
  }, [onClose]);

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleCloseDialog()}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto" onClose={handleCloseDialog}>
        <DialogHeader>
          <DialogTitle>{isEdit ? '编辑客户' : '新建客户'}</DialogTitle>
          <DialogDescription>
            {isEdit ? '修改客户信息' : '填写客户基本信息'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 基本信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="code">客户编码 *</Label>
              <Input
                id="code"
                value={formData.code}
                onChange={(e) => handleChange('code', e.target.value)}
                disabled={isEdit}
                placeholder="如: CUS001"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">客户名称 *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="请输入客户名称"
                required
              />
            </div>
          </div>

          {/* 联系信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact">联系人</Label>
              <Input
                id="contact"
                value={formData.contact || ''}
                onChange={(e) => handleChange('contact', e.target.value)}
                placeholder="请输入联系人姓名"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">联系电话</Label>
              <Input
                id="phone"
                value={formData.phone || ''}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="请输入联系电话"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">邮箱</Label>
            <Input
              id="email"
              type="email"
              value={formData.email || ''}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="请输入邮箱地址"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="address">地址</Label>
            <Input
              id="address"
              value={formData.address || ''}
              onChange={(e) => handleChange('address', e.target.value)}
              placeholder="请输入详细地址"
            />
          </div>

          {/* 财务信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tax_number">税号</Label>
              <Input
                id="tax_number"
                value={formData.tax_number || ''}
                onChange={(e) => handleChange('tax_number', e.target.value)}
                placeholder="请输入税号"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="bank_name">开户银行</Label>
              <Input
                id="bank_name"
                value={formData.bank_name || ''}
                onChange={(e) => handleChange('bank_name', e.target.value)}
                placeholder="请输入开户银行"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="bank_account">银行账号</Label>
              <Input
                id="bank_account"
                value={formData.bank_account || ''}
                onChange={(e) => handleChange('bank_account', e.target.value)}
                placeholder="请输入银行账号"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="credit_limit">信用额度</Label>
              <Input
                id="credit_limit"
                type="number"
                step="0.01"
                value={formData.credit_limit || ''}
                onChange={(e) => handleChange('credit_limit', parseFloat(e.target.value) || 0)}
                placeholder="请输入信用额度"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="payment_terms">付款条件（天数）</Label>
            <Input
              id="payment_terms"
              type="number"
              value={formData.payment_terms || ''}
              onChange={(e) => handleChange('payment_terms', parseInt(e.target.value) || undefined)}
              placeholder="如: 30"
            />
          </div>

          {/* 备注 */}
          <div className="space-y-2">
            <Label htmlFor="notes">备注</Label>
            <Textarea
              id="notes"
              value={formData.notes || ''}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="请输入备注信息"
              rows={3}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              取消
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '提交中...' : isEdit ? '保存' : '创建'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// 使用 memo 防止不必要的重新渲染
const CustomerFormDialogMemo = memo(CustomerFormDialog);
CustomerFormDialogMemo.displayName = 'CustomerFormDialog';

/**
 * 客户列表表格
 */
function CustomersTable({
  customers,
  onEdit,
  onDelete,
}: {
  customers: Customer[];
  onEdit: (customer: Customer) => void;
  onDelete: (customer: Customer) => void;
}) {
  if (customers.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Users className="w-12 h-12 text-muted-foreground mb-4" />
        <p className="text-muted-foreground">暂无客户数据</p>
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>编码</TableHead>
          <TableHead>名称</TableHead>
          <TableHead>联系人</TableHead>
          <TableHead>联系电话</TableHead>
          <TableHead>信用额度</TableHead>
          <TableHead>状态</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {customers.map((customer) => (
          <TableRow key={customer.id}>
            <TableCell className="font-medium">{customer.code}</TableCell>
            <TableCell>{customer.name}</TableCell>
            <TableCell>{customer.contact || '-'}</TableCell>
            <TableCell>{customer.phone || '-'}</TableCell>
            <TableCell>
              {customer.credit_limit ? `¥${customer.credit_limit.toLocaleString()}` : '-'}
            </TableCell>
            <TableCell>
              <CustomerStatusBadge status={customer.status} />
            </TableCell>
            <TableCell>
              {format(new Date(customer.created_at), 'yyyy-MM-dd')}
            </TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => onEdit(customer)}>
                  <Pencil className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(customer)}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/**
 * 加载骨架屏
 */
function CustomersSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>编码</TableHead>
          <TableHead>名称</TableHead>
          <TableHead>联系人</TableHead>
          <TableHead>联系电话</TableHead>
          <TableHead>信用额度</TableHead>
          <TableHead>状态</TableHead>
          <TableHead>创建时间</TableHead>
          <TableHead className="text-right">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3, 4, 5].map((i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-5 w-16" /></TableCell>
            <TableCell><Skeleton className="h-5 w-32" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
            <TableCell><Skeleton className="h-5 w-16" /></TableCell>
            <TableCell><Skeleton className="h-5 w-24" /></TableCell>
            <TableCell><Skeleton className="h-5 w-20" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/**
 * 页面主体
 */
export default function CustomersPage() {
  const queryClient = useQueryClient();
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | undefined>();

  // 获取客户列表
  const {
    data: customers = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['sales', 'customers', searchKeyword],
    queryFn: () => salesApi.getCustomers({ keyword: searchKeyword }),
  });

  // 创建客户
  const createMutation = useMutation({
    mutationFn: (data: CreateCustomerRequest) => salesApi.createCustomer(data),
    onSuccess: () => {
      toast.success('客户创建成功');
      setIsFormOpen(false);
      setEditingCustomer(undefined);
      queryClient.invalidateQueries({ queryKey: ['sales', 'customers'] });
    },
    onError: (error) => {
      toast.error('创建失败：' + (error as Error).message);
    },
  });

  // 更新客户
  const updateMutation = useMutation({
    mutationFn: ({ customerId, data }: { customerId: number; data: UpdateCustomerRequest }) =>
      salesApi.updateCustomer(customerId, data),
    onSuccess: () => {
      toast.success('客户更新成功');
      setIsFormOpen(false);
      setEditingCustomer(undefined);
      queryClient.invalidateQueries({ queryKey: ['sales', 'customers'] });
    },
    onError: (error) => {
      toast.error('更新失败：' + (error as Error).message);
    },
  });

  // 删除客户
  const deleteMutation = useMutation({
    mutationFn: (customerId: number) => salesApi.deleteCustomer(customerId),
    onSuccess: () => {
      toast.success('客户删除成功');
      setEditingCustomer(undefined);
      queryClient.invalidateQueries({ queryKey: ['sales', 'customers'] });
    },
    onError: (error) => {
      toast.error('删除失败：' + (error as Error).message);
    },
  });

  // 处理表单提交
  const handleFormSubmit = (data: CreateCustomerRequest | UpdateCustomerRequest) => {
    if (editingCustomer) {
      updateMutation.mutate({ customerId: editingCustomer.id, data });
    } else {
      createMutation.mutate(data as CreateCustomerRequest);
    }
  };

  // 处理编辑
  const handleEdit = (customer: Customer) => {
    setEditingCustomer(customer);
    setIsFormOpen(true);
  };

  // 处理删除
  const handleDelete = (customer: Customer) => {
    if (confirm(`确定要删除客户「${customer.name}」吗？`)) {
      deleteMutation.mutate(customer.id);
    }
  };

  // 处理新建
  const handleNew = () => {
    setEditingCustomer(undefined);
    setIsFormOpen(true);
  };

  // 处理搜索
  const handleSearch = () => {
    refetch();
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">客户管理</h1>
          <p className="text-muted-foreground mt-1">
            管理客户基本信息和联系方式
          </p>
        </div>
        <Button onClick={handleNew}>
          <Plus className="w-4 h-4 mr-2" />
          新建客户
        </Button>
      </div>

      {/* 搜索栏 */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <Input
              placeholder="搜索客户编码、名称、联系人..."
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="max-w-sm"
            />
            <Button onClick={handleSearch} variant="outline">
              <Search className="w-4 h-4 mr-2" />
              搜索
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 客户列表 */}
      <Card>
        <CardHeader>
          <CardTitle>客户列表</CardTitle>
          <CardDescription>
            共 {customers.length} 个客户
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <CustomersSkeleton />
          ) : error ? (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>加载失败</AlertTitle>
              <AlertDescription>
                加载客户列表失败，请稍后重试。
                <Button
                  variant="outline"
                  size="sm"
                  className="ml-2"
                  onClick={() => refetch()}
                >
                  重试
                </Button>
              </AlertDescription>
            </Alert>
          ) : (
            <CustomersTable
              customers={customers}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          )}
        </CardContent>
      </Card>

      {/* 表单对话框 */}
      <CustomerFormDialogMemo
        open={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingCustomer(undefined);
        }}
        onSubmit={handleFormSubmit}
        customer={editingCustomer}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
